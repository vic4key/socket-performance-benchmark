#!/usr/bin/env python3
"""
Remote Server Starter
Tự động start TCP và UDP servers trên máy remote
"""

import asyncio
import socket
import threading
import argparse
import sys
import signal
from tcp_benchmark import TCPBenchmark
from udp_benchmark import UDPBenchmark

class RemoteServer:
    def __init__(self, host='0.0.0.0', tcp_port=8888, udp_port=8889, data_size=1024, iterations=1000):
        self.host = host
        self.tcp_port = tcp_port
        self.udp_port = udp_port
        self.data_size = data_size
        self.iterations = iterations
        self.running = True
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n🛑 Received signal {signum}, shutting down servers...")
        self.running = False
    
    async def tcp_server(self):
        """Async TCP server"""
        print(f"🌐 Starting TCP Server on {self.host}:{self.tcp_port}")
        
        benchmark = TCPBenchmark(self.host, self.tcp_port, self.data_size, self.iterations)
        
        server = await asyncio.start_server(
            benchmark.handle_client, self.host, self.tcp_port
        )
        
        print(f"✅ TCP Server ready on {self.host}:{self.tcp_port}")
        
        async with server:
            await server.serve_forever()
    
    def udp_server(self):
        """UDP server"""
        print(f"🌐 Starting UDP Server on {self.host}:{self.udp_port}")
        
        benchmark = UDPBenchmark(self.host, self.udp_port, self.data_size, self.iterations)
        benchmark.server_running = True
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.host, self.udp_port))
        
        print(f"✅ UDP Server ready on {self.host}:{self.udp_port}")
        
        try:
            while self.running and benchmark.server_running:
                try:
                    data, addr = sock.recvfrom(self.data_size)
                    if len(data) == self.data_size:
                        sock.sendto(benchmark.test_data, addr)
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        print(f"❌ UDP Server error: {e}")
                    break
        except KeyboardInterrupt:
            pass
        finally:
            sock.close()
            print("🛑 UDP Server stopped")
    
    async def run_servers(self):
        """Run both TCP and UDP servers"""
        print("🚀 REMOTE SERVER STARTER")
        print("="*50)
        print(f"📍 Host: {self.host}")
        print(f"🔌 TCP Port: {self.tcp_port}")
        print(f"📡 UDP Port: {self.udp_port}")
        print(f"📊 Data size: {self.data_size} bytes")
        print("="*50)
        
        # Start UDP server in background thread
        udp_thread = threading.Thread(target=self.udp_server)
        udp_thread.daemon = True
        udp_thread.start()
        
        # Wait a bit for UDP server to start
        await asyncio.sleep(1)
        
        # Start TCP server in main thread
        try:
            await self.tcp_server()
        except KeyboardInterrupt:
            pass
        finally:
            self.running = False
            print("🛑 TCP Server stopped")

def main():
    parser = argparse.ArgumentParser(
        description="Remote Server Starter - Start TCP and UDP servers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start servers with default settings
  python benchmark_remote_server.py
  
  # Start servers on specific ports
  python benchmark_remote_server.py --tcp-port 8888 --udp-port 8889
  
  # Start servers on specific host
  python benchmark_remote_server.py --host 127.0.0.1
        """
    )
    
    parser.add_argument('--host', default='0.0.0.0',
                       help=f'Host address (default: 0.0.0.0')
    parser.add_argument('--tcp-port', type=int, default=8888,
                       help='TCP port (default: 8888)')
    parser.add_argument('--udp-port', type=int, default=8889,
                       help='UDP port (default: 8889)')
    parser.add_argument('--data-size', type=int, default=1024,
                       help='Data size in bytes (default: 1024 = 1KiB)')
    parser.add_argument('--iterations', type=int, default=1000,
                       help='Number of iterations (default: 1000)')
    
    args = parser.parse_args()
    
    server = RemoteServer(
        host=args.host,
        tcp_port=args.tcp_port,
        udp_port=args.udp_port,
        data_size=args.data_size,
        iterations=args.iterations
    )
    
    try:
        asyncio.run(server.run_servers())
    except KeyboardInterrupt:
        print("\n🛑 Server startup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error starting servers: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 