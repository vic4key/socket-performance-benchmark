import asyncio
import time
import statistics
import socket
import struct

class TCPBenchmark:
    def __init__(self, host='localhost', port=8888, data_size=1024, iterations=1000):
        self.host = host
        self.port = port
        self.data_size = data_size  # 1KiB
        self.iterations = iterations
        self.test_data = b'x' * data_size
        self.results = []
        
    async def tcp_server(self):
        """Async TCP server that receives data and sends back"""
        try:
            server = await asyncio.start_server(
                self.handle_client, self.host, self.port
            )
            
            print(f"TCP Server listening on {self.host}:{self.port}")
            
            async with server:
                await server.serve_forever()
        except OSError as e:
            if e.errno == 98:  # Address already in use
                print(f"TCP Server error: Port {self.port} is already in use")
            else:
                print(f"TCP Server error: {e}")
        except Exception as e:
            print(f"TCP Server error: {e}")
    
    async def handle_client(self, reader, writer):
        """Handle individual client connections"""
        addr = writer.get_extra_info('peername')
        print(f"TCP Client connected: {addr}")
        
        try:
            for i in range(self.iterations):
                # Receive data with timeout
                try:
                    data = await asyncio.wait_for(
                        reader.read(self.data_size),
                        timeout=5.0
                    )
                except asyncio.TimeoutError:
                    print(f"Warning: Timeout receiving data from client at iteration {i}")
                    break
                if len(data) == 0:  # Client disconnected
                    print(f"TCP Client disconnected early: {addr}")
                    break
                elif len(data) != self.data_size:
                    print(f"Warning: Received {len(data)} bytes, expected {self.data_size}")
                
                # Send data back with timeout
                try:
                    writer.write(self.test_data)
                    await asyncio.wait_for(writer.drain(), timeout=5.0)
                except asyncio.TimeoutError:
                    print(f"Warning: Timeout sending data to client at iteration {i}")
                    break
                
        except ConnectionResetError:
            print(f"TCP Client connection reset: {addr}")
        except BrokenPipeError:
            print(f"TCP Client broken pipe: {addr}")
        except Exception as e:
            print(f"TCP Server error: {e}")
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception as e:
                print(f"Error closing writer: {e}")
            print(f"TCP Client disconnected: {addr}")
    
    async def tcp_client(self):
        """Async TCP client that sends data and receives response"""
        print(f"TCP Client connecting to {self.host}:{self.port}")
        
        try:
            # Add timeout for connection
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port),
                timeout=10.0
            )
            
            for i in range(self.iterations):
                start_time = time.perf_counter()
                
                # Send data with timeout
                try:
                    writer.write(self.test_data)
                    await asyncio.wait_for(writer.drain(), timeout=5.0)
                except asyncio.TimeoutError:
                    print(f"Warning: Timeout sending data at iteration {i}")
                    break
                
                # Receive response with timeout
                try:
                    data = await asyncio.wait_for(
                        reader.read(self.data_size),
                        timeout=5.0
                    )
                except asyncio.TimeoutError:
                    print(f"Warning: Timeout receiving data at iteration {i}")
                    break
                
                end_time = time.perf_counter()
                duration = (end_time - start_time) * 1000  # Convert to milliseconds
                self.results.append(duration)
                
                if len(data) == 0:  # Server disconnected
                    print(f"Warning: Server disconnected at iteration {i}")
                    break
                elif len(data) != self.data_size:
                    print(f"Warning: Received {len(data)} bytes, expected {self.data_size}")
                
                # Progress indicator - update on same line every 10 iterations
                if (i + 1) % 10 == 0 or (i + 1) == self.iterations:
                    percent = ((i + 1) / self.iterations) * 100
                    print(f"\r📊 TCP Progress: {percent:5.1f}% ({i + 1}/{self.iterations})", end="", flush=True)
                
                # Small delay to prevent overwhelming
                await asyncio.sleep(0.001)
            
            writer.close()
            await writer.wait_closed()
            
        except ConnectionRefusedError:
            print(f"TCP Client error: Connection refused to {self.host}:{self.port}")
        except ConnectionResetError:
            print(f"TCP Client error: Connection reset by server")
        except BrokenPipeError:
            print(f"TCP Client error: Broken pipe")
        except Exception as e:
            print(f"TCP Client error: {e}")
    
    def get_result(self):
        """Get benchmark results as a dictionary"""
        if not self.results:
            return None
            
        total_time = sum(self.results)
        avg_time = statistics.mean(self.results)
        min_time = min(self.results)
        max_time = max(self.results)
        std_dev = statistics.stdev(self.results) if len(self.results) > 1 else 0
        
        total_data = self.iterations * self.data_size * 2  # Send + receive
        throughput = (total_data / 1024 / 1024) / (total_time / 1000)  # MB/s
        
        return {
            'total_time': total_time,
            'avg_time': avg_time,
            'min_time': min_time,
            'max_time': max_time,
            'std_dev': std_dev,
            'throughput': throughput,
            'total_data_mb': total_data / 1024 / 1024
        }
    
    def print_results(self):
        """Print benchmark results"""
        print()  # New line after progress indicator
        result = self.get_result()
        if not result:
            print("No results to display")
            return
            
        print("\n" + "="*50)
        print("TCP SOCKET BENCHMARK RESULTS")
        print("="*50)
        print(f"Data size per transfer: {self.data_size} bytes (1KiB)")
        print(f"Total iterations: {self.iterations}")
        print(f"Total data transferred: {result['total_data_mb']:.2f} MB")
        print(f"Total time: {result['total_time']:.2f} ms")
        print(f"Average time per transfer: {result['avg_time']:.3f} ms")
        print(f"Min time: {result['min_time']:.3f} ms")
        print(f"Max time: {result['max_time']:.3f} ms")
        print(f"Standard deviation: {result['std_dev']:.3f} ms")
        print(f"Throughput: {result['throughput']:.2f} MB/s")
        print("="*50)

async def run_tcp_benchmark():
    """Run TCP benchmark with server and client"""
    benchmark = TCPBenchmark()
    
    # Start server in background
    server_task = asyncio.create_task(benchmark.tcp_server())
    
    # Wait a bit for server to start
    await asyncio.sleep(1)
    
    # Run client
    await benchmark.tcp_client()
    
    # Cancel server
    server_task.cancel()
    
    # Print results
    benchmark.print_results()

if __name__ == "__main__":
    asyncio.run(run_tcp_benchmark()) 