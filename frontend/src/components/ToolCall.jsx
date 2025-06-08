import React from 'react';
import './ToolCall.css';

const ToolCall = ({ toolCall }) => {
    if (!toolCall) {
        return null;
    }

    return (
        <div className="tool-call-card">
            <div className="tool-call-header">
                <strong>Tool Called:</strong> <code>{toolCall.tool_name}</code>
            </div>
            <div className="tool-call-body">
                <p><strong>Parameters:</strong></p>
                <pre>{JSON.stringify(toolCall.parameters, null, 2)}</pre>
                <p><strong>Output:</strong></p>
                <pre>{toolCall.output}</pre>
            </div>
        </div>
    );
};

export default ToolCall; 