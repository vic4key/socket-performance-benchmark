#!/usr/bin/env python3
"""
Unified Socket Performance Benchmark Tool
Benchmarks Async TCP Socket and UDP Socket performance for both local and remote
"""

import asyncio
import time
import argparse
import sys
import socket
import subprocess
import platform
import threading
from tcp_benchmark import TCPBenchmark
from udp_benchmark import UDPBenchmark
from common import print_comparison_table, create_benchmark_result

class UnifiedBenchmark:
    def __init__(self, host='localhost', tcp_port=8888, udp_port=8889, data_size=1024, iterations=1000):
        self.host = host
        self.tcp_port = tcp_port
        self.udp_port = udp_port
        self.data_size = data_size
        self.iterations = iterations
        
    def check_network_connectivity(self):
        """Kiểm tra kết nối mạng cho remote benchmark"""
        if self.host == 'localhost':
            return True
            
        print("🔍 Kiểm tra kết nối mạng...")
        
        # Test ping
        try:
            if platform.system().lower() == "windows":
                cmd = ["ping", "-n", "2", self.host]
            else:
                cmd = ["ping", "-c", "2", self.host]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ Ping thành công đến {self.host}")
            else:
                print(f"⚠️ Ping không thành công đến {self.host}")
                return False
        except Exception as e:
            print(f"❌ Lỗi ping: {e}")
            return False
        
        # Test TCP port
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((self.host, self.tcp_port))
            sock.close()
            
            if result == 0:
                print(f"✅ TCP port {self.tcp_port} có thể kết nối")
            else:
                print(f"❌ TCP port {self.tcp_port} không thể kết nối")
                return False
        except Exception as e:
            print(f"❌ Lỗi test TCP port: {e}")
            return False
        
        # Test UDP port
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(5)
            sock.sendto(b"test", (self.host, self.udp_port))
            sock.close()
            print(f"✅ UDP port {self.udp_port} có thể kết nối")
        except Exception as e:
            print(f"⚠️ UDP port {self.udp_port} có thể không hoạt động: {e}")
        
        return True
    
    def run_tcp_benchmark(self):
        """Run TCP benchmark (local or remote)"""
        print(f"\n🔌 Chạy TCP benchmark đến {self.host}:{self.tcp_port}")
        
        benchmark = TCPBenchmark(self.host, self.tcp_port, self.data_size, self.iterations)
        
        if self.host == 'localhost':
            # Local mode: start server + run client
            async def run_local():
                # Start server in background
                server_task = asyncio.create_task(benchmark.tcp_server())
                
                # Wait a bit for server to start
                await asyncio.sleep(1)
                
                # Run client
                await benchmark.tcp_client()
                
                # Cancel server
                server_task.cancel()
                
                # Print results and return
                benchmark.print_results()
                return create_benchmark_result(benchmark, "TCP")
            
            return asyncio.run(run_local())
        else:
            # Remote mode: only run client (server should be running elsewhere)
            async def run_remote():
                print(f"✅ Connecting to remote TCP server at {self.host}:{self.tcp_port}")
                await benchmark.tcp_client()
                benchmark.print_results()
                return create_benchmark_result(benchmark, "TCP")
            
            return asyncio.run(run_remote())
    
    def run_udp_benchmark(self):
        """Run UDP benchmark (local or remote)"""
        print(f"\n📡 Chạy UDP benchmark đến {self.host}:{self.udp_port}")
        
        benchmark = UDPBenchmark(self.host, self.udp_port, self.data_size, self.iterations)
        
        if self.host == 'localhost':
            # Local mode: start server + run client
            # Start server in background thread
            server_thread = threading.Thread(target=benchmark.udp_server)
            server_thread.daemon = True
            server_thread.start()
            
            # Wait a bit for server to start
            time.sleep(1)
            
            # Run client
            benchmark.udp_client()
            
            # Stop server
            benchmark.server_running = False
            
            # Wait for server to stop
            server_thread.join(timeout=2)
            
            # Print results and return
            benchmark.print_results()
            return create_benchmark_result(benchmark, "UDP")
        else:
            # Remote mode: only run client (server should be running elsewhere)
            print(f"✅ Connecting to remote UDP server at {self.host}:{self.udp_port}")
            benchmark.udp_client()
            benchmark.print_results()
            return create_benchmark_result(benchmark, "UDP")
    
    def run_comparison_benchmark(self):
        """Run both benchmarks and compare results"""
        mode = "REMOTE" if self.host != 'localhost' else "LOCAL"
        print(f"\n🚀 {mode} SOCKET PERFORMANCE COMPARISON BENCHMARK")
        print("="*60)
        print(f"📍 Host: {self.host}")
        print(f"📊 Data size: {self.data_size} bytes ({self.data_size/1024:.1f} KiB)")
        print(f"🔄 Iterations: {self.iterations}")
        print("="*60)
        
        # Check network connectivity for remote
        if self.host != 'localhost' and not self.check_network_connectivity():
            print("❌ Không thể kết nối đến server. Kiểm tra lại kết nối mạng.")
            return False
        
        # Run TCP benchmark
        tcp_result = self.run_tcp_benchmark()
        
        # Run UDP benchmark
        udp_result = self.run_udp_benchmark()
        
        # Print comparison table
        print_comparison_table([tcp_result, udp_result])
        
        print("\n" + "="*60)
        print(f"✅ {mode} BENCHMARK COMPLETED")
        print("="*60)
        
        return True

def main():
    parser = argparse.ArgumentParser(
        description="Unified Socket Performance Benchmark Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Local benchmark (default)
  python benchmark_runner_unified.py --compare
  
  # Remote benchmark
  python benchmark_runner_unified.py --host 192.168.1.100 --compare
  
  # Single protocol
  python benchmark_runner_unified.py --tcp --host 192.168.1.100
  
  # Custom parameters
  python benchmark_runner_unified.py --host 192.168.1.100 --iterations 500 --data-size 2048
        """
    )
    
    parser.add_argument('--host', default='localhost',
                       help='Host address (default: localhost)')
    parser.add_argument('--tcp-port', type=int, default=8888,
                       help='TCP port (default: 8888)')
    parser.add_argument('--udp-port', type=int, default=8889,
                       help='UDP port (default: 8889)')
    parser.add_argument('--data-size', type=int, default=1024,
                       help='Data size in bytes (default: 1024 = 1KiB)')
    parser.add_argument('--iterations', type=int, default=1000,
                       help='Number of iterations (default: 1000)')
    parser.add_argument('--tcp', action='store_true',
                       help='Run TCP benchmark only')
    parser.add_argument('--udp', action='store_true',
                       help='Run UDP benchmark only')
    parser.add_argument('--compare', action='store_true',
                       help='Run both TCP and UDP benchmarks and compare')
    
    args = parser.parse_args()
    
    # If no specific benchmark is selected, run comparison by default
    if not (args.tcp or args.udp or args.compare):
        args.compare = True
    
    benchmark = UnifiedBenchmark(
        host=args.host,
        tcp_port=args.tcp_port,
        udp_port=args.udp_port,
        data_size=args.data_size,
        iterations=args.iterations
    )
    
    try:
        if args.tcp:
            benchmark.run_tcp_benchmark()
        elif args.udp:
            benchmark.run_udp_benchmark()
        elif args.compare:
            benchmark.run_comparison_benchmark()
            
    except KeyboardInterrupt:
        print("\n🛑 Benchmark interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error running benchmark: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 