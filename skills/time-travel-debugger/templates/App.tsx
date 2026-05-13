import { useCallback, useEffect, useState, useRef } from "react";
import { ReactFlow, MiniMap, Controls, Background, BackgroundVariant, useNodesState, useEdgesState, addEdge } from "@xyflow/react";
import dagre from "dagre";
import { Play, Pause, SkipBack, Trash2, Send } from "lucide-react";
import "@xyflow/react/dist/style.css";
import CustomNode from "./components/CustomNode";
import "./index.css";

const nodeTypes = { customNode: CustomNode };
const dagreGraph = new dagre.graphlib.Graph();
dagreGraph.setDefaultEdgeLabel(() => ({}));

export default function App() {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  
  const [code, setCode] = useState("#include <iostream>\nusing namespace std;\n\nvoid handleAdmin() {\n    cout << \"Welcome Admin!\" << endl;\n}\n\nvoid handleGuest() {\n    cout << \"Welcome Guest. Limited Access.\" << endl;\n}\n\nint main() {\n    int passcode = 0;\n    cout << \"Enter a passcode: \" << endl;\n    cin >> passcode;\n\n    if (passcode == 1234) {\n        handleAdmin();\n    } else {\n        handleGuest();\n    }\n    return 0;\n}");
  const [terminalOut, setTerminalOut] = useState("");
  const [stdinInput, setStdinInput] = useState("");
  
  const [traceHistory, setTraceHistory] = useState<{time: number, nodeId: string}[]>([]);
  const [playbackIndex, setPlaybackIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  const loadArchitecture = async () => {
    try {
      const res = await fetch("http://localhost:4001/architecture.json");
      const architectureData = await res.json();
      if (!architectureData.nodes) return;
      
      dagreGraph.setGraph({ rankdir: "TB", ranksep: 80, nodesep: 150 });
      architectureData.nodes.forEach((node: any) => dagreGraph.setNode(node.id, { width: 220, height: 100 }));
      architectureData.edges.forEach((edge: any) => dagreGraph.setEdge(edge.source, edge.target));
      dagre.layout(dagreGraph);
      
      const layoutedNodes = architectureData.nodes.map((node: any) => {
        const nodeWithPosition = dagreGraph.node(node.id);
        node.targetPosition = "top"; node.sourcePosition = "bottom";
        node.position = { x: nodeWithPosition.x - 110, y: nodeWithPosition.y - 50 };
        return node;
      });
      setNodes(layoutedNodes);
      setEdges(architectureData.edges);
    } catch(e) {}
  };

  useEffect(() => { loadArchitecture(); }, []);

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:4001");
    wsRef.current = ws;
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "trace_history") {
        setTraceHistory(data.data);
        if (data.data.length > 0) setPlaybackIndex(data.data.length - 1);
      } else if (data.type === "trace_update") {
        setTraceHistory(prev => {
          const newHistory = [...prev, data.data];
          setPlaybackIndex(current => current === prev.length - 1 || prev.length === 0 ? newHistory.length - 1 : current);
          return newHistory;
        });
      } else if (data.type === "stdout") {
        setTerminalOut(prev => prev + data.data);
      } else if (data.type === "reload_architecture") {
        loadArchitecture();
      }
    };
    return () => ws.close();
  }, []);

  useEffect(() => {
    let interval: any;
    if (isPlaying && traceHistory.length > 0) {
      interval = setInterval(() => {
        setPlaybackIndex(prev => {
          if (prev >= traceHistory.length - 1) { setIsPlaying(false); return prev; }
          return prev + 1;
        });
      }, 500);
    }
    return () => clearInterval(interval);
  }, [isPlaying, traceHistory.length]);

  const compileAndRun = async () => {
    setTerminalOut("Compiling...\n");
    setTraceHistory([]);
    setPlaybackIndex(0);
    try {
      const res = await fetch("http://localhost:4001/upload", {
        method: "POST", body: code
      });
      const text = await res.text();
      if (!res.ok) setTerminalOut(prev => prev + text + "\n");
    } catch(e) {
      setTerminalOut(prev => prev + "Network Error\n");
    }
  };

  const sendStdin = () => {
    if (wsRef.current && stdinInput) {
      wsRef.current.send(JSON.stringify({ type: "stdin", data: stdinInput }));
      setTerminalOut(prev => prev + "> " + stdinInput + "\n");
      setStdinInput("");
    }
  };

  const activeNodeId = traceHistory.length > 0 && playbackIndex < traceHistory.length ? traceHistory[playbackIndex].nodeId : null;
  const renderedNodes = nodes.map((node) => ({ ...node, data: { ...node.data, isActive: node.id === activeNodeId } }));
  const onConnect = useCallback((params: any) => setEdges((eds) => addEdge({ ...params, animated: true, type: "smoothstep" }, eds)), [setEdges]);

  return (
    <div style={{ width: "100vw", height: "100vh", display: "flex", backgroundColor: "#0f172a", color: "white" }}>
      <div style={{ width: "35%", display: "flex", flexDirection: "column", borderRight: "1px solid #334155" }}>
        
        <div style={{ flex: 1, display: "flex", flexDirection: "column", padding: 10 }}>
          <div style={{display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10}}>
            <h3 style={{margin:0, color:"#38bdf8"}}>C++ Web IDE</h3>
            <button onClick={compileAndRun} style={{background: "#3b82f6", color: "white", padding: "8px 16px", borderRadius: 4, border: "none", cursor: "pointer", fontWeight: "bold"}}>
              Compile & Run
            </button>
          </div>
          <textarea 
            value={code} 
            onChange={e => setCode(e.target.value)}
            spellCheck="false"
            style={{flex: 1, backgroundColor: "#1e293b", color: "#e2e8f0", padding: 15, fontFamily: "monospace", border: "1px solid #475569", borderRadius: 6, resize: "none"}}
          />
        </div>

        <div style={{ height: "35%", display: "flex", flexDirection: "column", padding: 10, borderTop: "1px solid #334155", backgroundColor: "#020617" }}>
          <h4 style={{margin: "0 0 5px 0", color: "#94a3b8"}}>Terminal Output</h4>
          <pre style={{flex: 1, margin: 0, overflowY: "auto", whiteSpace: "pre-wrap", color: "#4ade80", fontSize: 13}}>
            {terminalOut}
          </pre>
          <div style={{display: "flex", marginTop: 10}}>
            <input 
              value={stdinInput} 
              onChange={e => setStdinInput(e.target.value)} 
              onKeyDown={e => e.key === "Enter" && sendStdin()}
              placeholder="Type input here..." 
              style={{flex: 1, background: "#1e293b", color: "white", border: "1px solid #475569", padding: "8px", borderRadius: "4px 0 0 4px"}}
            />
            <button onClick={sendStdin} style={{background: "#10b981", color: "white", border: "none", padding: "0 15px", borderRadius: "0 4px 4px 0", cursor: "pointer"}}><Send size={16}/></button>
          </div>
        </div>

      </div>

      <div style={{ width: "65%", position: "relative", display: "flex", flexDirection: "column" }}>
        <div style={{ flex: 1, position: "relative" }}>
          <ReactFlow nodes={renderedNodes} edges={edges} onNodesChange={onNodesChange} onEdgesChange={onEdgesChange} onConnect={onConnect} nodeTypes={nodeTypes} fitView colorMode="dark">
            <Controls />
            <Background variant={BackgroundVariant.Dots} gap={16} size={2} color="#334155" />
          </ReactFlow>
        </div>
        
        <div className="vcr-bar">
          <div className="vcr-controls">
            <button onClick={() => setPlaybackIndex(0)} className="vcr-btn"><SkipBack size={20} /></button>
            <button onClick={() => setIsPlaying(!isPlaying)} className="vcr-btn vcr-play-btn">
              {isPlaying ? <Pause size={24} /> : <Play size={24} />}
            </button>
            <button onClick={() => { setTraceHistory([]); setPlaybackIndex(0); }} className="vcr-btn vcr-danger"><Trash2 size={20} /></button>
          </div>
          
          <div className="vcr-timeline-container">
            <span className="vcr-time">{playbackIndex} / {Math.max(0, traceHistory.length - 1)}</span>
            <input 
              type="range" min={0} max={Math.max(0, traceHistory.length - 1)} value={playbackIndex} 
              onChange={(e) => { setPlaybackIndex(parseInt(e.target.value)); setIsPlaying(false); }} 
              className="vcr-slider" 
            />
          </div>
        </div>
      </div>
    </div>
  );
}
