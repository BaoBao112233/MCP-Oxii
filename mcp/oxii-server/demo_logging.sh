#!/bin/bash

# Quick demo script for MCP Oxii-server tool logging

echo "🔧 MCP Oxii-server Tool Logging Demo"
echo "======================================"

# Check if server is running
echo "📡 Checking if MCP server is running..."
if curl -s http://localhost:9031/health > /dev/null 2>&1; then
    echo "✅ MCP server is running on port 9031"
else
    echo "❌ MCP server not running. Start with:"
    echo "   cd /home/baobao/Projects/MCP-Oxii-Work/MCP-Oxii/mcp/oxii-server"
    echo "   python main.py"
    exit 1
fi

echo ""
echo "📊 Current Tool Statistics:"
curl -s http://localhost:9031/stats | python3 -m json.tool | head -20

echo ""
echo "🔍 Recent Tool Logs (last 5):"
curl -s http://localhost:9031/logs | python3 -c "
import sys, json
data = json.load(sys.stdin)
logs = data.get('logs', [])
for log in logs[-5:]:
    print(f'  📝 {log}')
"

echo ""
echo "🛠️  Available Tools:"
curl -s http://localhost:9031/docs.json | python3 -c "
import sys, json
data = json.load(sys.stdin)
tools = data.get('tools', [])
for i, tool in enumerate(tools, 1):
    print(f'  {i}. {tool[\"name\"]} - {tool.get(\"description\", \"No description\")}')
"

echo ""
echo "🌐 Web Interface:"
echo "  📊 Documentation: http://localhost:9031/docx"
echo "  📈 Statistics: http://localhost:9031/stats"  
echo "  📋 Logs: http://localhost:9031/logs"
echo "  ❤️  Health: http://localhost:9031/health"

echo ""
echo "🧪 Test Commands:"
echo "  python test_logging.py"
echo "  curl http://localhost:9031/stats"
echo "  curl -X POST http://localhost:9031/stats/reset"