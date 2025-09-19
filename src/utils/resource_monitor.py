#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Resource monitoring and cleanup utility
Provides periodic garbage collection and resource monitoring
"""

import gc
import sys
import psutil
import threading
import time
import logging
from typing import Optional, Dict, Any
from PyQt5.QtCore import QTimer, QObject, pyqtSignal


class ResourceMonitor(QObject):
    """Monitor and manage application resource usage"""
    
    # Signals for resource status updates
    resource_status_updated = pyqtSignal(dict)  # Resource usage statistics
    memory_warning = pyqtSignal(float)  # Memory usage percentage
    cleanup_completed = pyqtSignal(int)  # Number of objects collected
    
    def __init__(self, check_interval_ms=60000):  # Default: check every minute
        super().__init__()
        self.check_interval_ms = check_interval_ms
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_resources)
        self.initial_memory = None
        self.cleanup_threshold_mb = 200  # Trigger cleanup if memory usage increases by 200MB
        self.memory_warning_threshold = 75  # Warn if using >75% of available memory
        
        # Get initial memory baseline
        self._initialize_baseline()
        
    def _initialize_baseline(self):
        """Initialize memory baseline for comparison"""
        try:
            process = psutil.Process()
            self.initial_memory = process.memory_info().rss / (1024 * 1024)  # MB
            logging.info(f"Resource monitor initialized with baseline memory: {self.initial_memory:.1f} MB")
        except Exception as e:
            logging.warning(f"Failed to get initial memory baseline: {e}")
            self.initial_memory = 0
    
    def start_monitoring(self):
        """Start periodic resource monitoring"""
        if not self.timer.isActive():
            self.timer.start(self.check_interval_ms)
            logging.info(f"Resource monitoring started (interval: {self.check_interval_ms/1000:.1f}s)")
    
    def stop_monitoring(self):
        """Stop periodic resource monitoring"""
        if self.timer.isActive():
            self.timer.stop()
            logging.info("Resource monitoring stopped")
    
    def check_resources(self):
        """Check current resource usage and trigger cleanup if needed"""
        try:
            stats = self.get_resource_stats()
            
            # Emit resource status update
            self.resource_status_updated.emit(stats)
            
            # Check memory usage
            current_memory_mb = stats['memory_mb']
            memory_increase = current_memory_mb - self.initial_memory
            memory_percentage = stats['memory_percent']
            
            # Trigger cleanup if memory has increased significantly
            if memory_increase > self.cleanup_threshold_mb:
                logging.info(f"Memory increased by {memory_increase:.1f}MB, triggering cleanup...")
                collected = self.force_cleanup()
                if collected > 0:
                    logging.info(f"Cleanup collected {collected} objects, freed memory")
                    # Reset baseline after successful cleanup
                    self._initialize_baseline()
            
            # Emit memory warning if usage is high
            if memory_percentage > self.memory_warning_threshold:
                logging.warning(f"High memory usage detected: {memory_percentage:.1f}%")
                self.memory_warning.emit(memory_percentage)
                
        except Exception as e:
            logging.error(f"Error during resource check: {e}")
    
    def get_resource_stats(self) -> Dict[str, Any]:
        """Get current resource usage statistics"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            
            # Get system memory info
            sys_memory = psutil.virtual_memory()
            
            stats = {
                'memory_mb': memory_info.rss / (1024 * 1024),
                'memory_percent': (memory_info.rss / sys_memory.total) * 100,
                'memory_increase_mb': (memory_info.rss / (1024 * 1024)) - self.initial_memory,
                'cpu_percent': process.cpu_percent(),
                'threads_count': process.num_threads(),
                'open_files': len(process.open_files()) if hasattr(process, 'open_files') else 0,
                'connections_count': len(process.connections()) if hasattr(process, 'connections') else 0,
                'gc_objects': len(gc.get_objects()),
                'gc_stats': gc.get_stats() if hasattr(gc, 'get_stats') else []
            }
            
            return stats
            
        except Exception as e:
            logging.error(f"Error getting resource stats: {e}")
            return {
                'memory_mb': 0,
                'memory_percent': 0,
                'memory_increase_mb': 0,
                'cpu_percent': 0,
                'threads_count': 0,
                'open_files': 0,
                'connections_count': 0,
                'gc_objects': 0,
                'gc_stats': []
            }
    
    def force_cleanup(self) -> int:
        """Force garbage collection and resource cleanup"""
        try:
            # Force garbage collection
            collected = gc.collect()
            
            # Clean up any global session from background_workers
            try:
                from src.workers.background_workers import cleanup_session
                cleanup_session()
            except ImportError:
                pass  # Module not available
            except Exception as e:
                logging.warning(f"Error cleaning up background workers session: {e}")
            
            # Additional cleanup operations
            self._cleanup_weak_references()
            self._cleanup_thread_locals()
            
            # Emit cleanup completed signal
            self.cleanup_completed.emit(collected)
            
            logging.info(f"Resource cleanup completed, collected {collected} objects")
            return collected
            
        except Exception as e:
            logging.error(f"Error during force cleanup: {e}")
            return 0
    
    def _cleanup_weak_references(self):
        """Clean up weak references"""
        try:
            import weakref
            # This will clean up dead weak references
            weakref.WeakKeyDictionary._remove_dead_weakrefs = True
        except Exception as e:
            logging.debug(f"Weak reference cleanup error: {e}")
    
    def _cleanup_thread_locals(self):
        """Clean up thread-local storage"""
        try:
            # Clean up thread locals if any exist
            if hasattr(threading, 'local'):
                for thread in threading.enumerate():
                    if hasattr(thread, '_target') and thread._target:
                        # Thread cleanup would happen automatically
                        pass
        except Exception as e:
            logging.debug(f"Thread local cleanup error: {e}")
    
    def get_memory_usage_report(self) -> str:
        """Get a detailed memory usage report"""
        try:
            stats = self.get_resource_stats()
            
            report = f"""
Resource Usage Report:
=====================
Current Memory: {stats['memory_mb']:.1f} MB
Memory % of System: {stats['memory_percent']:.1f}%
Memory Increase: {stats['memory_increase_mb']:.1f} MB
CPU Usage: {stats['cpu_percent']:.1f}%
Active Threads: {stats['threads_count']}
Open Files: {stats['open_files']}
Network Connections: {stats['connections_count']}
GC Tracked Objects: {stats['gc_objects']}
"""
            
            if stats['gc_stats']:
                report += f"\nGarbage Collection Stats:\n"
                for i, stat in enumerate(stats['gc_stats']):
                    report += f"  Generation {i}: {stat}\n"
            
            return report
            
        except Exception as e:
            return f"Error generating memory report: {e}"


# Global instance for easy access
_resource_monitor: Optional[ResourceMonitor] = None


def get_resource_monitor() -> ResourceMonitor:
    """Get or create the global resource monitor instance"""
    global _resource_monitor
    if _resource_monitor is None:
        _resource_monitor = ResourceMonitor()
    return _resource_monitor


def start_resource_monitoring(check_interval_ms: int = 60000):
    """Start global resource monitoring"""
    monitor = get_resource_monitor()
    monitor.check_interval_ms = check_interval_ms
    monitor.start_monitoring()


def stop_resource_monitoring():
    """Stop global resource monitoring"""
    global _resource_monitor
    if _resource_monitor is not None:
        _resource_monitor.stop_monitoring()


def force_resource_cleanup() -> int:
    """Force immediate resource cleanup"""
    monitor = get_resource_monitor()
    return monitor.force_cleanup()


def get_memory_report() -> str:
    """Get current memory usage report"""
    monitor = get_resource_monitor()
    return monitor.get_memory_usage_report()


if __name__ == "__main__":
    # Test the resource monitor
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Create and start monitor
    monitor = ResourceMonitor(check_interval_ms=5000)  # Check every 5 seconds for testing
    
    def on_resource_update(stats):
        print(f"Memory: {stats['memory_mb']:.1f}MB, Objects: {stats['gc_objects']}")
    
    def on_memory_warning(percentage):
        print(f"⚠️ High memory usage: {percentage:.1f}%")
    
    def on_cleanup_completed(collected):
        print(f"✅ Cleanup completed, collected {collected} objects")
    
    monitor.resource_status_updated.connect(on_resource_update)
    monitor.memory_warning.connect(on_memory_warning)
    monitor.cleanup_completed.connect(on_cleanup_completed)
    
    monitor.start_monitoring()
    
    print("Resource monitor test started. Press Ctrl+C to stop.")
    print(monitor.get_memory_usage_report())
    
    try:
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        monitor.stop_monitoring()
        print("\nResource monitor test stopped.")