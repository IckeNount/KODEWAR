"use client";

import { Editor } from "@monaco-editor/react";

interface CodeEditorProps {
  initialCode: string;
  onChange?: (value: string | undefined) => void;
}

export default function CodeEditor({ initialCode, onChange }: CodeEditorProps) {
  return (
    <Editor
      height='100%'
      defaultLanguage='python'
      defaultValue={initialCode}
      theme='vs-dark'
      onChange={onChange}
      options={{
        minimap: { enabled: false },
        fontSize: 14,
        lineNumbers: "on",
        roundedSelection: false,
        scrollBeyondLastLine: false,
        automaticLayout: true,
      }}
    />
  );
}
