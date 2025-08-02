import socket
import time
import statistics
import struct
import threading

class UDPBenchmark:
    def __init__(self, host='localhost', port=8889, data_size=1024, iterations=1000):
        self.host = host
        self.port = port
        self.data_size = data_size  # 1KiB
        self.iterations = iterations
        self.test_data = b'x' * data_size
        self.results = []
        self.server_running = False
        
    def udp_server(self):
        """UDP server that receives data and sends back"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.host, self.port))
        
        print(f"UDP Server listening on {self.host}:{self.port}")
        self.server_running = True
        
        try:
            while self.server_running:
                try:
                    data, addr = sock.recvfrom(self.data_size)
                    if len(data) == self.data_size:
                        # Send data back
                        sock.sendto(self.test_data, addr)
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.server_running:
                        print(f"UDP Server error: {e}")
                    break
        finally:
            sock.close()
            print("UDP Server stopped")
    
    def udp_client(self):
        """UDP client that sends data and receives response"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5.0)  # 5 second timeout
        
        print(f"UDP Client connecting to {self.host}:{self.port}")
        
        try:
            for i in range(self.iterations):
                start_time = time.perf_counter()
                
                # Send data
                sock.sendto(self.test_data, (self.host, self.port))
                
                # Receive response
                data, addr = sock.recvfrom(self.data_size)
                
                end_time = time.perf_counter()
                duration = (end_time - start_time) * 1000  # Convert to milliseconds
                self.results.append(duration)
                
                if len(data) != self.data_size:
                    print(f"Warning: Received {len(data)} bytes, expected {self.data_size}")
                
                # Progress indicator - update on same line every 10 iterations
                if (i + 1) % 10 == 0 or (i + 1) == self.iterations:
                    percent = ((i + 1) / self.iterations) * 100
                    print(f"\r📊 UDP Progress: {percent:5.1f}% ({i + 1}/{self.iterations})", end="", flush=True)
                
                # Small delay to prevent overwhelming
                time.sleep(0.001)
                
        except Exception as e:
            print(f"UDP Client error: {e}")
        finally:
            sock.close()
    
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
        print("UDP SOCKET BENCHMARK RESULTS")
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

def run_udp_benchmark():
    """Run UDP benchmark with server and client"""
    benchmark = UDPBenchmark()
    
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
    
    # Print results
    benchmark.print_results()

if __name__ == "__main__":
    run_udp_benchmark() 