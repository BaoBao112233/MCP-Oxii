# 🔧 MCP Oxii-server Tool Logging System

## 📋 Overview

MCP Oxii-server bây giờ bao gồm hệ thống logging toàn diện để theo dõi tất cả các tool calls, giúp debug và monitoring.

## 🚀 Features

### ✅ **Tool Call Logging**
- **Real-time logging** tất cả tool calls với arguments và results
- **Error tracking** với detailed error messages
- **Success/failure statistics** cho từng tool
- **Timestamp tracking** cho mỗi tool call

### ✅ **Statistics Tracking**
- **Total call count** across all tools  
- **Per-tool statistics** including success/error rates
- **Last called timestamp** cho mỗi tool
- **Server uptime** tracking

### ✅ **Web Endpoints**
- `/health` - Health check
- `/stats` - Tool usage statistics (JSON)
- `/logs` - Recent tool call logs
- `/stats/reset` - Reset statistics (POST)
- `/docx` - Enhanced documentation với logging info

## 🔍 **Log Format**

### **Tool Call Started:**
```
🔧🚀 TOOL_CALLED - tool_name with args: {"arg1": "value1", "arg2": "value2"}
```

### **Tool Call Success:**
```
🔧✅ TOOL_CALL_SUCCESS - Tool: tool_name | Args: {...} | Result: {...}
```

### **Tool Call Error:**
```
🔧❌ TOOL_CALL_ERROR - Tool: tool_name | Args: {...} | Error: error_message
```

## 📊 **Usage Examples**

### **1. View Current Statistics**
```bash
curl http://localhost:9031/stats
```

**Response:**
```json
{
  "total_calls": 15,
  "tool_calls": {
    "get_device_list": {
      "count": 8,
      "last_called": "2025-10-22T10:30:15.123456",
      "success_count": 7,
      "error_count": 1
    },
    "switch_device_control": {
      "count": 7,
      "last_called": "2025-10-22T10:25:30.654321",
      "success_count": 6,
      "error_count": 1
    }
  },
  "start_time": "2025-10-22T09:00:00.000000",
  "current_time": "2025-10-22T10:30:30.789012"
}
```

### **2. View Recent Logs**
```bash
curl http://localhost:9031/logs
```

**Response:**
```json
{
  "logs": [
    "2025-10-22 10:30:15,123 - __main__ - INFO - 🔧🚀 TOOL_CALLED - get_device_list with args: {\"room\": \"living room\"}",
    "2025-10-22 10:30:15,456 - __main__ - INFO - 🔧✅ TOOL_CALL_SUCCESS - Tool: get_device_list | Args: {\"room\": \"living room\"} | Result: [{\"name\": \"Smart Light\", \"status\": \"on\"}]"
  ],
  "total_lines": 50
}
```

### **3. Reset Statistics**
```bash
curl -X POST http://localhost:9031/stats/reset
```

### **4. View Enhanced Documentation**
```bash
# Open in browser
http://localhost:9031/docx
```

## 🛠️ **Development & Debugging**

### **1. Start Server with Logging**
```bash
cd mcp/oxii-server
python main.py
```

### **2. Test Logging System**
```bash
python test_logging.py
```

### **3. Monitor Real-time Logs**
```bash
# Follow log file (in Docker)
docker exec -f mcp-oxii-server tail -f /var/log/supervisor/mcp-tools.log

# Follow stdout logs
docker logs -f mcp-oxii-server
```

### **4. Check Tool Usage**
```bash
# Quick stats check
curl -s http://localhost:9031/stats | jq '.tool_calls'

# Most used tools
curl -s http://localhost:9031/stats | jq '.tool_calls | to_entries | sort_by(.value.count) | reverse'
```

## 📈 **Monitoring Integration**

### **Prometheus Metrics Format**
Có thể dễ dàng convert stats sang Prometheus format:

```python
# Example converter
def stats_to_prometheus(stats):
    metrics = []
    metrics.append(f"mcp_total_calls {stats['total_calls']}")
    
    for tool_name, tool_stats in stats['tool_calls'].items():
        metrics.append(f"mcp_tool_calls{{tool=\"{tool_name}\"}} {tool_stats['count']}")
        metrics.append(f"mcp_tool_success{{tool=\"{tool_name}\"}} {tool_stats['success_count']}")
        metrics.append(f"mcp_tool_errors{{tool=\"{tool_name}\"}} {tool_stats['error_count']}")
    
    return "\n".join(metrics)
```

### **Grafana Dashboard Queries**
```promql
# Total tool calls
sum(mcp_tool_calls)

# Error rate by tool  
sum(rate(mcp_tool_errors[5m])) by (tool)

# Most active tools
topk(5, sum(rate(mcp_tool_calls[5m])) by (tool))
```

## 🔧 **Troubleshooting**

### **Issue: Logs not appearing**
```bash
# Check log file permissions
ls -la /var/log/supervisor/mcp-tools.log

# Check if supervisor directory exists
mkdir -p /var/log/supervisor
```

### **Issue: Stats not updating**
```bash
# Check if tool wrapper is working
curl http://localhost:9031/stats
# Should show increasing counts after tool calls
```

### **Issue: High error rates**
```bash
# Check recent error logs
curl http://localhost:9031/logs | jq '.logs[] | select(contains("ERROR"))'

# Check specific tool errors
curl http://localhost:9031/stats | jq '.tool_calls[] | select(.error_count > 0)'
```

## 🎯 **Best Practices**

1. **Regular Monitoring**: Check `/stats` endpoint regularly
2. **Error Tracking**: Monitor error_count for each tool
3. **Performance**: High call counts may indicate optimization opportunities
4. **Debugging**: Use `/logs` endpoint for detailed troubleshooting
5. **Cleanup**: Reset stats periodically with `/stats/reset`

## 🔄 **Future Enhancements**

- [ ] Real-time WebSocket logging stream
- [ ] Performance metrics (execution time per tool)
- [ ] Alert system for high error rates
- [ ] Log rotation and archival
- [ ] Integration with external monitoring systems
- [ ] Custom log filtering and search

## 📝 **Implementation Details**

### **Log Wrapper Function**
```python
def create_logged_tool(original_func: Callable) -> Callable:
    """Create a wrapper that logs tool calls"""
    # Wraps both sync and async functions
    # Preserves original function metadata
    # Logs before and after execution
    # Tracks success/error statistics
```

### **Statistics Storage**
```python
tool_stats = {
    "total_calls": 0,
    "tool_calls": {
        "tool_name": {
            "count": 0,
            "last_called": "timestamp",
            "success_count": 0,
            "error_count": 0
        }
    },
    "start_time": "timestamp"
}
```

### **Log File Location**
- **Docker**: `/var/log/supervisor/mcp-tools.log`
- **Local**: Falls back to stdout/stderr
- **Format**: Standard Python logging format với custom emojis

---

Hệ thống logging này giúp theo dõi và debug MCP Oxii-server một cách hiệu quả! 🎉