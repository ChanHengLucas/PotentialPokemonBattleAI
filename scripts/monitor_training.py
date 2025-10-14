#!/usr/bin/env python3
"""
PokéAI Training Monitor

Monitors the self-training process and provides real-time updates
on progress, performance, and system health.
"""

import json
import logging
import time
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import psutil
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrainingMonitor:
    """Monitors training progress and system health"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.training_data_dir = Path("data/training")
        self.reports_dir = Path("data/reports")
        self.monitoring_active = False
        
    def start_monitoring(self, interval: int = 30) -> None:
        """Start monitoring training progress"""
        logger.info(f"Starting training monitoring (interval: {interval}s)")
        self.monitoring_active = True
        
        try:
            while self.monitoring_active:
                # Check training progress
                progress = self.check_training_progress()
                
                # Check system health
                system_health = self.check_system_health()
                
                # Check service health
                service_health = self.check_service_health()
                
                # Generate monitoring report
                report = {
                    "timestamp": datetime.now().isoformat(),
                    "progress": progress,
                    "system_health": system_health,
                    "service_health": service_health,
                    "overall_status": self.determine_overall_status(progress, system_health, service_health)
                }
                
                # Save monitoring data
                self.save_monitoring_data(report)
                
                # Print status update
                self.print_status_update(report)
                
                # Wait for next check
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Monitoring error: {e}")
            raise
        
        logger.info("Training monitoring stopped")
    
    def check_training_progress(self) -> Dict[str, Any]:
        """Check current training progress"""
        progress = {
            "cycles_completed": 0,
            "games_played": 0,
            "current_score": 0.0,
            "improvement_rate": 0.0,
            "training_duration": 0.0,
            "status": "unknown"
        }
        
        # Check training history
        history_file = self.training_data_dir / "training_history.json"
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    history = json.load(f)
                
                if history:
                    progress["cycles_completed"] = len(history)
                    progress["games_played"] = sum(cycle.get("games_played", 0) for cycle in history)
                    progress["training_duration"] = sum(cycle.get("duration", 0) for cycle in history)
                    
                    # Get current best score
                    if history:
                        progress["current_score"] = history[-1].get("best_team_score", 0.0)
                        
                        # Calculate improvement rate
                        if len(history) > 1:
                            scores = [cycle.get("best_team_score", 0.0) for cycle in history]
                            if len(scores) > 1:
                                progress["improvement_rate"] = (scores[-1] - scores[0]) / len(scores)
                    
                    # Determine status
                    if progress["cycles_completed"] > 0:
                        progress["status"] = "active"
                    else:
                        progress["status"] = "idle"
                        
            except Exception as e:
                logger.warning(f"Error reading training history: {e}")
        
        return progress
    
    def check_system_health(self) -> Dict[str, Any]:
        """Check system health metrics"""
        health = {
            "cpu_usage": psutil.cpu_percent(interval=1),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "load_average": psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0.0,
            "status": "healthy"
        }
        
        # Determine health status
        if health["cpu_usage"] > 90 or health["memory_usage"] > 90 or health["disk_usage"] > 90:
            health["status"] = "critical"
        elif health["cpu_usage"] > 80 or health["memory_usage"] > 80 or health["disk_usage"] > 80:
            health["status"] = "warning"
        
        return health
    
    def check_service_health(self) -> Dict[str, Any]:
        """Check health of required services"""
        services = {
            "calc_service": {"url": "http://localhost:3001/health", "status": "unknown"},
            "policy_service": {"url": "http://localhost:8000/health", "status": "unknown"},
            "teambuilder_service": {"url": "http://localhost:8001/health", "status": "unknown"}
        }
        
        for service_name, service_info in services.items():
            try:
                response = requests.get(service_info["url"], timeout=5)
                if response.status_code == 200:
                    services[service_name]["status"] = "healthy"
                else:
                    services[service_name]["status"] = "unhealthy"
            except requests.exceptions.RequestException:
                services[service_name]["status"] = "unreachable"
        
        return services
    
    def determine_overall_status(self, progress: Dict[str, Any], system_health: Dict[str, Any], service_health: Dict[str, Any]) -> str:
        """Determine overall training status"""
        # Check if training is active
        if progress["status"] != "active":
            return "idle"
        
        # Check system health
        if system_health["status"] == "critical":
            return "critical"
        
        # Check service health
        service_statuses = [service["status"] for service in service_health.values()]
        if "unreachable" in service_statuses:
            return "service_issues"
        elif "unhealthy" in service_statuses:
            return "service_warning"
        
        # Check training progress
        if progress["improvement_rate"] < -0.1:
            return "degrading"
        elif progress["improvement_rate"] > 0.1:
            return "improving"
        else:
            return "stable"
    
    def save_monitoring_data(self, report: Dict[str, Any]) -> None:
        """Save monitoring data"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        monitoring_file = self.reports_dir / f"monitoring_{timestamp}.json"
        
        with open(monitoring_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Keep only recent monitoring files
        self.cleanup_old_monitoring_files()
    
    def cleanup_old_monitoring_files(self, days: int = 7) -> None:
        """Clean up old monitoring files"""
        cutoff_time = datetime.now() - timedelta(days=days)
        
        for file_path in self.reports_dir.glob("monitoring_*.json"):
            try:
                file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_time < cutoff_time:
                    file_path.unlink()
            except Exception as e:
                logger.warning(f"Error cleaning up {file_path}: {e}")
    
    def print_status_update(self, report: Dict[str, Any]) -> None:
        """Print status update"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        status = report["overall_status"]
        
        # Status emoji
        status_emoji = {
            "idle": "😴",
            "active": "🔄",
            "improving": "📈",
            "stable": "✅",
            "degrading": "📉",
            "service_issues": "⚠️",
            "service_warning": "⚠️",
            "critical": "🚨"
        }
        
        emoji = status_emoji.get(status, "❓")
        
        print(f"\n[{timestamp}] {emoji} Training Status: {status.upper()}")
        
        # Progress info
        progress = report["progress"]
        if progress["cycles_completed"] > 0:
            print(f"  Cycles: {progress['cycles_completed']}, Games: {progress['games_played']}")
            print(f"  Score: {progress['current_score']:.3f}, Improvement: {progress['improvement_rate']:+.3f}")
        
        # System health
        system = report["system_health"]
        print(f"  System: CPU {system['cpu_usage']:.1f}%, RAM {system['memory_usage']:.1f}%, Disk {system['disk_usage']:.1f}%")
        
        # Service health
        services = report["service_health"]
        service_status = []
        for service_name, service_info in services.items():
            status = service_info["status"]
            if status == "healthy":
                service_status.append(f"{service_name}: ✅")
            elif status == "unhealthy":
                service_status.append(f"{service_name}: ⚠️")
            else:
                service_status.append(f"{service_name}: ❌")
        
        print(f"  Services: {', '.join(service_status)}")
    
    def generate_monitoring_report(self) -> Dict[str, Any]:
        """Generate comprehensive monitoring report"""
        logger.info("Generating monitoring report")
        
        # Load recent monitoring data
        monitoring_files = sorted(self.reports_dir.glob("monitoring_*.json"))
        if not monitoring_files:
            return {"error": "No monitoring data found"}
        
        # Load last 24 hours of data
        cutoff_time = datetime.now() - timedelta(hours=24)
        recent_files = []
        
        for file_path in monitoring_files:
            try:
                file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_time > cutoff_time:
                    recent_files.append(file_path)
            except Exception:
                continue
        
        if not recent_files:
            return {"error": "No recent monitoring data found"}
        
        # Analyze monitoring data
        monitoring_data = []
        for file_path in recent_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                monitoring_data.append(data)
            except Exception as e:
                logger.warning(f"Error loading {file_path}: {e}")
                continue
        
        if not monitoring_data:
            return {"error": "No valid monitoring data found"}
        
        # Generate report
        report = {
            "report_timestamp": datetime.now().isoformat(),
            "data_points": len(monitoring_data),
            "time_range": {
                "start": monitoring_data[0]["timestamp"],
                "end": monitoring_data[-1]["timestamp"]
            },
            "overall_status": monitoring_data[-1]["overall_status"],
            "progress_summary": self.analyze_progress(monitoring_data),
            "system_summary": self.analyze_system_health(monitoring_data),
            "service_summary": self.analyze_service_health(monitoring_data),
            "recommendations": self.generate_recommendations(monitoring_data)
        }
        
        # Save report
        report_file = self.reports_dir / "monitoring_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Monitoring report saved to {report_file}")
        return report
    
    def analyze_progress(self, monitoring_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze training progress from monitoring data"""
        progress_data = [data["progress"] for data in monitoring_data]
        
        if not progress_data:
            return {"error": "No progress data"}
        
        # Calculate averages
        avg_score = sum(p.get("current_score", 0) for p in progress_data) / len(progress_data)
        avg_improvement = sum(p.get("improvement_rate", 0) for p in progress_data) / len(progress_data)
        
        # Find trends
        scores = [p.get("current_score", 0) for p in progress_data]
        if len(scores) > 1:
            score_trend = "improving" if scores[-1] > scores[0] else "degrading"
        else:
            score_trend = "stable"
        
        return {
            "average_score": avg_score,
            "average_improvement_rate": avg_improvement,
            "score_trend": score_trend,
            "total_cycles": max(p.get("cycles_completed", 0) for p in progress_data),
            "total_games": max(p.get("games_played", 0) for p in progress_data)
        }
    
    def analyze_system_health(self, monitoring_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze system health from monitoring data"""
        system_data = [data["system_health"] for data in monitoring_data]
        
        if not system_data:
            return {"error": "No system health data"}
        
        # Calculate averages
        avg_cpu = sum(s.get("cpu_usage", 0) for s in system_data) / len(system_data)
        avg_memory = sum(s.get("memory_usage", 0) for s in system_data) / len(system_data)
        avg_disk = sum(s.get("disk_usage", 0) for s in system_data) / len(system_data)
        
        # Count status occurrences
        status_counts = {}
        for s in system_data:
            status = s.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "average_cpu_usage": avg_cpu,
            "average_memory_usage": avg_memory,
            "average_disk_usage": avg_disk,
            "status_distribution": status_counts
        }
    
    def analyze_service_health(self, monitoring_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze service health from monitoring data"""
        service_data = [data["service_health"] for data in monitoring_data]
        
        if not service_data:
            return {"error": "No service health data"}
        
        # Analyze each service
        service_analysis = {}
        for service_name in ["calc_service", "policy_service", "teambuilder_service"]:
            service_statuses = [s.get(service_name, {}).get("status", "unknown") for s in service_data]
            
            status_counts = {}
            for status in service_statuses:
                status_counts[status] = status_counts.get(status, 0) + 1
            
            service_analysis[service_name] = {
                "status_distribution": status_counts,
                "health_percentage": status_counts.get("healthy", 0) / len(service_statuses) * 100
            }
        
        return service_analysis
    
    def generate_recommendations(self, monitoring_data: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on monitoring data"""
        recommendations = []
        
        # Analyze system health
        system_data = [data["system_health"] for data in monitoring_data]
        if system_data:
            avg_cpu = sum(s.get("cpu_usage", 0) for s in system_data) / len(system_data)
            avg_memory = sum(s.get("memory_usage", 0) for s in system_data) / len(system_data)
            
            if avg_cpu > 80:
                recommendations.append("High CPU usage detected - consider reducing training intensity")
            if avg_memory > 80:
                recommendations.append("High memory usage detected - consider increasing system memory")
        
        # Analyze service health
        service_data = [data["service_health"] for data in monitoring_data]
        if service_data:
            for service_name in ["calc_service", "policy_service", "teambuilder_service"]:
                service_statuses = [s.get(service_name, {}).get("status", "unknown") for s in service_data]
                unhealthy_count = sum(1 for status in service_statuses if status != "healthy")
                
                if unhealthy_count > len(service_statuses) * 0.2:
                    recommendations.append(f"{service_name} showing instability - check service logs")
        
        # Analyze training progress
        progress_data = [data["progress"] for data in monitoring_data]
        if progress_data:
            scores = [p.get("current_score", 0) for p in progress_data]
            if len(scores) > 1 and scores[-1] < scores[0]:
                recommendations.append("Training performance declining - consider adjusting parameters")
        
        return recommendations

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Monitor PokéAI training")
    parser.add_argument("--interval", type=int, default=30, help="Monitoring interval in seconds")
    parser.add_argument("--report", action="store_true", help="Generate monitoring report")
    parser.add_argument("--config", default="config/self_training.json", help="Configuration file")
    
    args = parser.parse_args()
    
    # Load configuration
    config_file = Path(args.config)
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
    else:
        config = {}
    
    # Create monitor
    monitor = TrainingMonitor(config)
    
    if args.report:
        # Generate monitoring report
        report = monitor.generate_monitoring_report()
        
        if "error" in report:
            print(f"Error generating report: {report['error']}")
        else:
            print("\n=== Training Monitoring Report ===")
            print(f"Overall Status: {report['overall_status']}")
            print(f"Data Points: {report['data_points']}")
            print(f"Time Range: {report['time_range']['start']} to {report['time_range']['end']}")
            
            if "progress_summary" in report:
                progress = report["progress_summary"]
                print(f"\nProgress Summary:")
                print(f"  Average Score: {progress.get('average_score', 0):.3f}")
                print(f"  Score Trend: {progress.get('score_trend', 'unknown')}")
                print(f"  Total Cycles: {progress.get('total_cycles', 0)}")
                print(f"  Total Games: {progress.get('total_games', 0)}")
            
            if "recommendations" in report and report["recommendations"]:
                print(f"\nRecommendations:")
                for rec in report["recommendations"]:
                    print(f"  - {rec}")
    else:
        # Start monitoring
        monitor.start_monitoring(args.interval)

if __name__ == "__main__":
    main()
