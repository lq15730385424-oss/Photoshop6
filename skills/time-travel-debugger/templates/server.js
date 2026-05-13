import dgram from "dgram";
import { WebSocketServer } from "ws";
import http from "http";
import { spawn, exec } from "child_process";
import fs from "fs";
import path from "path";

const udpServer = dgram.createSocket("udp4");
const wss = new WebSocketServer({ noServer: true });

let clients = [];
let traceHistory = [];
let cppProcess = null;

const server = http.createServer((req, res) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, GET, OPTIONS");

  if (req.method === "OPTIONS") { res.writeHead(200); return res.end(); }

  if (req.url === "/architecture.json" && req.method === "GET") {
      try {
          const data = fs.readFileSync("architecture.json");
          res.writeHead(200, { "Content-Type": "application/json" });
          return res.end(data);
      } catch(e) {
          res.writeHead(404); return res.end("{}");
      }
  }

  if (req.url === "/upload" && req.method === "POST") {
    let body = "";
    req.on("data", chunk => body += chunk.toString());
    req.on("end", () => {
      
      let targetFile = "parser/target.cpp";
      body = body.trim();
      
      if (body.endsWith(".cpp") && !body.includes("\n")) {
          try {
             if (!fs.existsSync(body)) {
                 res.writeHead(400); return res.end("File not found: " + body);
             }
             targetFile = body;
          } catch (e) {
             res.writeHead(400); return res.end("Error reading file: " + body);
          }
      } else {
          fs.writeFileSync(targetFile, body);
      }

      traceHistory = [];
      broadcast({ type: "trace_history", data: traceHistory });
      
      const absoluteTarget = path.resolve(targetFile);
      
      exec(`cd parser && ./venv/bin/python parse_cpp.py "${absoluteTarget}"`, (err, stdout, stderr) => {
         if (err) { res.writeHead(500); return res.end("Parse Error: " + stderr); }
         
         const tracedFile = targetFile.replace(".cpp", "_traced.cpp");
         const absoluteTraced = path.resolve(tracedFile);
         const absoluteApp = path.resolve("parser/target_app");
         
         exec(`g++ "${absoluteTraced}" -o "${absoluteApp}"`, (err2, stdout2, stderr2) => {
             if (err2) { res.writeHead(500); return res.end("Compile Error: " + stderr2); }
             
             broadcast({ type: "reload_architecture" });

             if (cppProcess) cppProcess.kill();
             cppProcess = spawn(absoluteApp);
             
             cppProcess.stdout.on("data", (data) => broadcast({ type: "stdout", data: data.toString() }));
             cppProcess.stderr.on("data", (data) => broadcast({ type: "stdout", data: "ERROR: " + data.toString() }));
             cppProcess.on("close", (code, signal) => {
                 if (!signal) broadcast({ type: "stdout", data: "\n--- Process Finished ---\n" });
             });

             res.writeHead(200);
             res.end("Success");
         });
      });
    });
  }
});

server.on("upgrade", (request, socket, head) => {
  wss.handleUpgrade(request, socket, head, (ws) => { wss.emit("connection", ws, request); });
});

wss.on("connection", (ws) => {
  clients.push(ws);
  ws.send(JSON.stringify({ type: "trace_history", data: traceHistory }));
  
  ws.on("message", (msg) => {
    const command = JSON.parse(msg);
    if (command.type === "stdin" && cppProcess) {
      cppProcess.stdin.write(command.data + "\n");
    }
  });
  ws.on("close", () => { clients = clients.filter(c => c !== ws); });
});

function broadcast(obj) {
  clients.forEach(c => { if (c.readyState === 1) c.send(JSON.stringify(obj)); });
}

udpServer.on("message", (msg) => {
  const nodeId = msg.toString();
  traceHistory.push({ time: Date.now(), nodeId });
  broadcast({ type: "trace_update", data: { time: Date.now(), nodeId } });
});

udpServer.bind(4000);
server.listen(4001, () => console.log("Web IDE Server Running on 4001..."));
