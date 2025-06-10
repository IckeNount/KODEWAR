"use client";

import { useEffect, useRef } from "react";
import * as monaco from "monaco-editor";
import { editor } from "monaco-editor";

interface MonacoEditorProps {
  onMount: (editor: editor.IStandaloneCodeEditor) => void;
}

export function MonacoEditor({ onMount }: MonacoEditorProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);

  useEffect(() => {
    if (containerRef.current && !editorRef.current) {
      editorRef.current = monaco.editor.create(containerRef.current, {
        value: "",
        language: "python",
        theme: "vs-dark",
        minimap: { enabled: false },
        automaticLayout: true,
        fontSize: 14,
        lineNumbers: "on",
        scrollBeyondLastLine: false,
        tabSize: 4,
      });

      onMount(editorRef.current);
    }

    return () => {
      editorRef.current?.dispose();
    };
  }, [onMount]);

  return <div ref={containerRef} className='h-full' />;
}
