# 🚀 Socket Performance Benchmark

Performance benchmarking for Async TCP Socket and UDP Socket

## 💻 System Requirements

- 🐍 Python 3.7+
- 🖥️ Operating System: Windows, Linux, macOS
- 📦 No external dependencies required

## 💳 License
- 📰 Released under the [MIT](LICENSE) license
- ©️ Copyright © Vic P. & Vibe Coding ❤️

## 🎯 Usage

### 🏠 Local Benchmark Comparison
```bash
python benchmark_runner.py --compare --iterations 1000
```

### 🌐 Remote Benchmark Comparison

To test in real-world environment with 2 different machines:

#### ⬆️ Server Side (E.g., 192.168.1.100):
```bash
python benchmark_remote_server.py
```

#### ⬇️ Client Side
```bash
python benchmark_runner.py --compare --iterations 1000 --host 192.168.1.100
```

## 📖 Parameters (Optional)
<details>
<summary>Click here to view more ...</summary>

📃 Parameters

- `--tcp`: Run TCP benchmark only
- `--udp`: Run UDP benchmark only
- `--compare`: Run both benchmarks and compare results
- `--host`: Host address (default: localhost)
- `--data-size`: Data size in bytes (default: 1024 = 1KiB)
- `--iterations`: Number of iterations (default: 1000)

⚙️ Custom parameter examples

```bash
# Run TCP benchmark only
python benchmark_runner.py --tcp

# Run UDP benchmark only
python benchmark_runner.py --udp

# Run with 500 iterations
python benchmark_runner.py --compare --iterations 500

# Run with 2KiB data size
python benchmark_runner.py --compare --data-size 2048
```

💻 Command Line (for additional testing with iperf3)

```bash
iperf3 -s -p 8888
iperf3 -c 192.168.1.5 -p 8888 -l 1024 -f M

iperf3 -s -p 8889
iperf3 -c 192.168.1.5 -p 8889 -u -l 1024 -f M
```
</details>

## 📰 Results

### 🏠 Local Benchmark Results

| Protocol | Total Time (ms) | Throughput (MB/s) | Avg Time (ms) | Min Time (ms) | Max Time (ms) |
|----------|----------------|-------------------|---------------|---------------|---------------|
| TCP      | 703.73         | 2.78              | 0.704         | 0.151         | 2.407         |
| UDP      | 1028.80        | 1.90              | 1.029         | 0.305         | 3.005         |

**Performance Analysis:**
- **🚀 TCP is 31.6% faster than UDP**
- **⚡ TCP has 46.2% higher throughput than UDP**

### 🌐 Remote Benchmark Results (via LAN)

| Protocol | Total Time (ms) | Throughput (MB/s) | Avg Time (ms) | Min Time (ms) | Max Time (ms) | Std Dev (ms) |
|----------|----------------|-------------------|---------------|---------------|---------------|--------------|
| TCP      | 7717.18        | 0.25              | 7.717         | 4.099         | 21.789        | 1.837        |
| UDP      | 4111.68        | 0.48              | 4.112         | 2.508         | 27.319        | 1.761        |

**Performance Analysis:**
- **🚀 UDP is 46.7% faster than TCP** (opposite of local results)
- **⚡ UDP has 87.7% higher throughput than TCP**

### 🎯 Real-World Implications

**📊 Performance Summary:**
- **Local Environment:** TCP dominates (31.6% faster, 46.2% higher throughput)
- **Remote Environment:** UDP dominates (46.7% faster, 87.7% higher throughput)
- **Latency Impact:** TCP degraded 11x, UDP only 4x when going remote

**🔧 When to Choose TCP:**
- ✅ **Network applications:** File transfers, databases, web servers
- ✅ **Reliability-critical:** Banking, e-commerce, data integrity matters
- ✅ **High-throughput local:** Microservices on same machine/rack
- ✅ **Guaranteed delivery:** Email, file sync, backup systems
- ❌ **Avoid for:** Real-time gaming, video streaming over remote (LAN, Internet, etc)

**⚡ When to Choose UDP:**
- ✅ **Network applications:** Gaming, live streaming, VoIP
- ✅ **Real-time systems:** Chat, notifications, live updates
- ✅ **High-frequency trading:** Low latency critical
- ✅ **IoT/Sensor networks:** Battery efficiency, simple protocols
- ✅ **Distributed systems:** Service discovery, health checks

**🎯 Architecture Decisions:**
- **Microservices:** UDP for health checks, TCP for data sync
- **Gaming:** UDP for gameplay, TCP for chat/lobby
- **Streaming:** UDP for video/audio, TCP for control/metadata
- **IoT:** UDP for sensors, TCP for configuration updates

## 📬 Contact
Feel free to contact via [Twitter](https://twitter.com/vic4key) / [Gmail](mailto:vic4key@gmail.com) / [Blog](https://blog.vic.onl/) / [Website](https://vic.onl/)

