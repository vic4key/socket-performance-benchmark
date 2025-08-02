#!/usr/bin/env python3
"""
Common utilities for socket benchmarks
Shared code between local and remote benchmarks
"""

class BenchmarkResult:
    """Common benchmark result class"""
    def __init__(self, protocol, total_time, throughput, avg_time, min_time, max_time):
        self.protocol = protocol
        self.total_time = total_time
        self.throughput = throughput
        self.avg_time = avg_time
        self.min_time = min_time
        self.max_time = max_time

def print_comparison_table(results):
    """Print comparison table of benchmark results"""
    print("\n" + "="*80)
    print("BENCHMARK COMPARISON SUMMARY")
    print("="*80)
    
    # Table header
    print(f"{'Protocol':<12} {'Total Time (ms)':<15} {'Throughput (MB/s)':<18} {'Avg Time (ms)':<15} {'Min Time (ms)':<15} {'Max Time (ms)':<15}")
    print("-" * 80)
    
    # Table rows
    for result in results:
        if result:  # Only print if result exists
            print(f"{result.protocol:<12} {result.total_time:<15.2f} {result.throughput:<18.2f} {result.avg_time:<15.3f} {result.min_time:<15.3f} {result.max_time:<15.3f}")
    
    print("="*80)
    
    # Performance analysis
    valid_results = [r for r in results if r]
    if len(valid_results) == 2:
        tcp_result = valid_results[0]
        udp_result = valid_results[1]
        
        print("\nPERFORMANCE ANALYSIS:")
        print("-" * 40)
        
        # Speed comparison
        if udp_result.total_time < tcp_result.total_time:
            speed_diff = ((tcp_result.total_time - udp_result.total_time) / tcp_result.total_time) * 100
            print(f"UDP is {speed_diff:.1f}% faster than TCP")
        else:
            speed_diff = ((udp_result.total_time - tcp_result.total_time) / udp_result.total_time) * 100
            print(f"TCP is {speed_diff:.1f}% faster than UDP")
        
        # Throughput comparison
        if udp_result.throughput > tcp_result.throughput:
            throughput_diff = ((udp_result.throughput - tcp_result.throughput) / tcp_result.throughput) * 100
            print(f"UDP has {throughput_diff:.1f}% higher throughput than TCP")
        else:
            throughput_diff = ((tcp_result.throughput - udp_result.throughput) / udp_result.throughput) * 100
            print(f"TCP has {throughput_diff:.1f}% higher throughput than UDP")
        
        # Consistency comparison (lower std dev = more consistent)
        tcp_consistency = (tcp_result.max_time - tcp_result.min_time) / tcp_result.avg_time * 100
        udp_consistency = (udp_result.max_time - udp_result.min_time) / udp_result.avg_time * 100
        
        if tcp_consistency < udp_consistency:
            print(f"TCP has {(udp_consistency - tcp_consistency):.1f}% more consistent performance")
        else:
            print(f"UDP has {(tcp_consistency - udp_consistency):.1f}% more consistent performance")

def create_benchmark_result(benchmark, protocol):
    """Create BenchmarkResult from benchmark data"""
    result = benchmark.get_result()
    if result:
        return BenchmarkResult(protocol, result['total_time'], result['throughput'], 
                             result['avg_time'], result['min_time'], result['max_time'])
    return None 