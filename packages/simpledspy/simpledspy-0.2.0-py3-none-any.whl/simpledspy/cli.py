#!/usr/bin/env python3
import sys
import argparse
from simpledspy import pipe
from .optimization_manager import OptimizationManager

def main():
    parser = argparse.ArgumentParser(description="SimpleDSPy command line interface")
    parser.add_argument('inputs', nargs='*', help="Input strings to process (use - for stdin)")
    parser.add_argument('-d', '--description', help="Description of the processing task")
    parser.add_argument('--optimize', action='store_true', help="Enable optimization")
    parser.add_argument('--strategy', choices=['bootstrap_few_shot', 'mipro'], 
                       default='bootstrap_few_shot', help="Optimization strategy")
    parser.add_argument('--max-demos', type=int, default=4, 
                       help="Maximum number of demonstrations")
    parser.add_argument('--metric', type=str,
                       help="Custom metric function to use for optimization")
    
    args = parser.parse_args()
    
    # Configure optimization if enabled
    if args.optimize:
        from simpledspy import OptimizationManager
        optimizer = OptimizationManager()
        optimizer.configure(
            strategy=args.strategy,
            max_bootstrapped_demos=args.max_demos,
            max_labeled_demos=args.max_demos
        )
        # TODO: Add training data loading and optimization
    
    # Check if stdin has data
    if not sys.stdin.isatty():
        inputs = [line.strip() for line in sys.stdin]
    else:
        inputs = args.inputs
    # print("inputs:", inputs)
        
    # Process inputs
    result = pipe(*inputs, description=args.description)
    
    # Print results
    if isinstance(result, tuple):
        for res in result:
            print(res)
    else:
        print(result)

if __name__ == "__main__":
    main()
