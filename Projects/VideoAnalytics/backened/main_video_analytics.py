# Real-Time Video Analytics with Collaborative Agents
# File: main.py

import asyncio
import cv2
import numpy as np
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from queue import Queue
import threading
from collections import deque
import logging
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== CORE DATA STRUCTURES =====

@dataclass
class Detection:
    """Represents an object detection with bounding box and confidence"""
    class_id: int
    class_name: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # (x, y, width, height)
    timestamp: datetime

@dataclass
class Alert:
    """Represents a system alert"""
    alert_type: str
    severity: int  # 1-5, 5 being most severe
    description: str
    confidence: float
    timestamp: datetime
    frame_id: int

@dataclass
class FrameAnalysis:
    """Complete analysis results for a frame"""
    frame_id: int
    timestamp: datetime
    detections: List[Detection]
    alerts: List[Alert]
    agent_results: Dict[str, Any]
    processing_time: float

# ===== ABSTRACT BASE CLASSES =====

class BaseAgent(ABC):
    """Abstract base class for all AI agents"""
    
    def __init__(self, name: str):
        self.name = name
        self.is_initialized = False
        self.processing_times = deque(maxlen=100)  # Keep last 100 processing times
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the agent (load models, etc.)"""
        pass
    
    @abstractmethod
    def process_frame(self, frame: np.ndarray, frame_id: int) -> Dict[str, Any]:
        """Process a single frame and return results"""
        pass
    
    def get_average_processing_time(self) -> float:
        """Get average processing time in milliseconds"""
        if not self.processing_times:
            return 0.0
        return sum(self.processing_times) / len(self.processing_times)

# ===== INDIVIDUAL AI AGENTS =====

class ObjectDetectionAgent(BaseAgent):
    """Agent responsible for detecting objects in video frames"""
    
    def __init__(self):
        super().__init__("ObjectDetection")
        self.confidence_threshold = 0.5
        self.class_names = [
            'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus',
            'train', 'truck', 'boat', 'traffic light', 'fire hydrant',
            'stop sign', 'parking meter', 'bench'
        ]
        # Simulated model weights - in real implementation, load actual YOLO/DETR model
        self.model_weights = None
    
    def initialize(self) -> bool:
        """Initialize YOLO or similar object detection model"""
        try:
            # In a real implementation, you would load actual model weights:
            # self.model = YOLO('yolov8n.pt') or similar
            logger.info(f"Initializing {self.name} agent...")
            
            # Simulate model loading time
            time.sleep(1)
            
            # For demo purposes, we'll simulate detections
            self.is_initialized = True
            logger.info(f"{self.name} agent initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize {self.name} agent: {e}")
            return False
    
    def process_frame(self, frame: np.ndarray, frame_id: int) -> Dict[str, Any]:
        """Detect objects in the frame"""
        start_time = time.time()
        
        if not self.is_initialized:
            return {"error": "Agent not initialized", "detections": []}
        
        # Simulate object detection processing
        # In real implementation, this would be: results = self.model(frame)
        detections = self._simulate_object_detection(frame, frame_id)
        
        processing_time = (time.time() - start_time) * 1000  # Convert to ms
        self.processing_times.append(processing_time)
        
        return {
            "detections": detections,
            "processing_time": processing_time,
            "confidence_threshold": self.confidence_threshold
        }
    
    def _simulate_object_detection(self, frame: np.ndarray, frame_id: int) -> List[Detection]:
        """Simulate object detection - replace with real model inference"""
        height, width = frame.shape[:2]
        detections = []
        
        # Simulate finding objects based on frame characteristics
        # This is a simplified simulation for demo purposes
        np.random.seed(frame_id)  # Consistent results for same frame
        
        num_objects = np.random.randint(1, 4)  # 1-3 objects per frame
        
        for i in range(num_objects):
            # Random object properties
            class_idx = np.random.randint(0, len(self.class_names))
            confidence = np.random.uniform(0.6, 0.95)
            
            # Random bounding box
            x = np.random.randint(0, width // 2)
            y = np.random.randint(0, height // 2)
            w = np.random.randint(50, min(200, width - x))
            h = np.random.randint(50, min(200, height - y))
            
            if confidence >= self.confidence_threshold:
                detection = Detection(
                    class_id=class_idx,
                    class_name=self.class_names[class_idx],
                    confidence=confidence,
                    bbox=(x, y, w, h),
                    timestamp=datetime.now()
                )
                detections.append(detection)
        
        return detections

class MotionAnalysisAgent(BaseAgent):
    """Agent responsible for analyzing motion patterns and tracking"""
    
    def __init__(self):
        super().__init__("MotionAnalysis")
        self.previous_frame = None
        self.motion_threshold = 30.0
        self.tracking_data = {}  # Store tracking information
    
    def initialize(self) -> bool:
        """Initialize motion analysis components"""
        try:
            logger.info(f"Initializing {self.name} agent...")
            
            # Initialize background subtractor for motion detection
            self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
                detectShadows=True
            )
            
            self.is_initialized = True
            logger.info(f"{self.name} agent initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize {self.name} agent: {e}")
            return False
    
    def process_frame(self, frame: np.ndarray, frame_id: int) -> Dict[str, Any]:
        """Analyze motion in the frame"""
        start_time = time.time()
        
        if not self.is_initialized:
            return {"error": "Agent not initialized", "motion_data": {}}
        
        # Convert to grayscale for motion analysis
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply background subtraction
        fg_mask = self.bg_subtractor.apply(gray_frame)
        
        # Calculate motion intensity
        motion_intensity = self._calculate_motion_intensity(fg_mask)
        
        # Detect motion patterns
        motion_patterns = self._analyze_motion_patterns(fg_mask, frame_id)
        
        processing_time = (time.time() - start_time) * 1000
        self.processing_times.append(processing_time)
        
        return {
            "motion_intensity": motion_intensity,
            "motion_patterns": motion_patterns,
            "processing_time": processing_time,
            "has_significant_motion": motion_intensity > self.motion_threshold
        }
    
    def _calculate_motion_intensity(self, fg_mask: np.ndarray) -> float:
        """Calculate the intensity of motion in the frame"""
        # Count non-zero pixels (motion pixels)
        motion_pixels = np.count_nonzero(fg_mask)
        total_pixels = fg_mask.shape[0] * fg_mask.shape[1]
        
        # Return percentage of pixels with motion
        return (motion_pixels / total_pixels) * 100.0
    
    def _analyze_motion_patterns(self, fg_mask: np.ndarray, frame_id: int) -> Dict[str, Any]:
        """Analyze patterns in the motion"""
        # Find contours of moving objects
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        patterns = {
            "num_moving_objects": len([c for c in contours if cv2.contourArea(c) > 100]),
            "largest_motion_area": max([cv2.contourArea(c) for c in contours], default=0),
            "motion_regions": []
        }
        
        # Analyze each significant contour
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 100:  # Filter small noise
                x, y, w, h = cv2.boundingRect(contour)
                patterns["motion_regions"].append({
                    "bbox": (x, y, w, h),
                    "area": area
                })
        
        return patterns

class AnomalyDetectionAgent(BaseAgent):
    """Agent responsible for detecting anomalies and generating alerts"""
    
    def __init__(self):
        super().__init__("AnomalyDetection")
        self.baseline_data = deque(maxlen=100)  # Store baseline for comparison
        self.alert_threshold = 0.7
        self.frame_history = deque(maxlen=10)  # Store recent frame analyses
    
    def initialize(self) -> bool:
        """Initialize anomaly detection models"""
        try:
            logger.info(f"Initializing {self.name} agent...")
            
            # In real implementation, load pre-trained anomaly detection model
            # self.anomaly_model = load_isolation_forest_model()
            
            self.is_initialized = True
            logger.info(f"{self.name} agent initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize {self.name} agent: {e}")
            return False
    
    def process_frame(self, frame: np.ndarray, frame_id: int, 
                     context: Dict[str, Any]) -> Dict[str, Any]:
        """Detect anomalies based on frame and context from other agents"""
        start_time = time.time()
        
        if not self.is_initialized:
            return {"error": "Agent not initialized", "alerts": []}
        
        # Extract features for anomaly detection
        features = self._extract_features(frame, context)
        
        # Detect anomalies
        anomaly_score = self._calculate_anomaly_score(features)
        alerts = self._generate_alerts(anomaly_score, features, frame_id)
        
        # Update baseline data
        self.baseline_data.append(features)
        
        processing_time = (time.time() - start_time) * 1000
        self.processing_times.append(processing_time)
        
        return {
            "anomaly_score": anomaly_score,
            "alerts": alerts,
            "processing_time": processing_time,
            "features": features
        }
    
    def _extract_features(self, frame: np.ndarray, context: Dict[str, Any]) -> Dict[str, float]:
        """Extract features for anomaly detection"""
        features = {}
        
        # Basic frame statistics
        features["brightness"] = np.mean(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
        features["contrast"] = np.std(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
        
        # Context from other agents
        if "object_detection" in context:
            obj_results = context["object_detection"]
            features["num_detections"] = len(obj_results.get("detections", []))
            features["avg_confidence"] = np.mean([
                d.confidence for d in obj_results.get("detections", [])
            ]) if obj_results.get("detections") else 0.0
        
        if "motion_analysis" in context:
            motion_results = context["motion_analysis"]
            features["motion_intensity"] = motion_results.get("motion_intensity", 0.0)
            features["num_moving_objects"] = motion_results.get("motion_patterns", {}).get("num_moving_objects", 0)
        
        return features
    
    def _calculate_anomaly_score(self, features: Dict[str, float]) -> float:
        """Calculate anomaly score based on features"""
        if len(self.baseline_data) < 10:  # Need baseline data
            return 0.0
        
        # Simple anomaly detection based on deviation from baseline
        baseline_features = {}
        for key in features:
            baseline_values = [b.get(key, 0) for b in self.baseline_data if key in b]
            if baseline_values:
                baseline_features[key] = {
                    "mean": np.mean(baseline_values),
                    "std": np.std(baseline_values)
                }
        
        # Calculate deviation score
        total_deviation = 0.0
        num_features = 0
        
        for key, value in features.items():
            if key in baseline_features:
                mean = baseline_features[key]["mean"]
                std = baseline_features[key]["std"]
                
                if std > 0:
                    deviation = abs(value - mean) / std
                    total_deviation += min(deviation, 3.0)  # Cap at 3 standard deviations
                    num_features += 1
        
        return total_deviation / max(num_features, 1)
    
    def _generate_alerts(self, anomaly_score: float, features: Dict[str, float], 
                        frame_id: int) -> List[Alert]:
        """Generate alerts based on anomaly score and features"""
        alerts = []
        
        # High anomaly score alert
        if anomaly_score > self.alert_threshold:
            alerts.append(Alert(
                alert_type="high_anomaly",
                severity=min(5, int(anomaly_score * 2) + 1),
                description=f"High anomaly detected (score: {anomaly_score:.2f})",
                confidence=min(1.0, anomaly_score),
                timestamp=datetime.now(),
                frame_id=frame_id
            ))
        
        # Specific feature-based alerts
        if features.get("motion_intensity", 0) > 50:
            alerts.append(Alert(
                alert_type="high_motion",
                severity=3,
                description=f"High motion activity detected ({features['motion_intensity']:.1f}%)",
                confidence=0.8,
                timestamp=datetime.now(),
                frame_id=frame_id
            ))
        
        if features.get("num_detections", 0) > 5:
            alerts.append(Alert(
                alert_type="crowd_detected",
                severity=2,
                description=f"Large number of objects detected ({features['num_detections']})",
                confidence=0.7,
                timestamp=datetime.now(),
                frame_id=frame_id
            ))
        
        return alerts

# ===== MULTI-AGENT COORDINATOR =====

class AgentCoordinator:
    """Coordinates multiple AI agents for collaborative video analysis"""
    
    def __init__(self):
        self.agents = {
            "object_detection": ObjectDetectionAgent(),
            "motion_analysis": MotionAnalysisAgent(),
            "anomaly_detection": AnomalyDetectionAgent()
        }
        self.consensus_threshold = 2  # Minimum agreements for high-confidence results
        self.frame_counter = 0
        self.processing_stats = {
            "total_frames": 0,
            "total_processing_time": 0.0,
            "agent_stats": {}
        }
    
    def initialize_all_agents(self) -> bool:
        """Initialize all agents"""
        logger.info("Initializing all agents...")
        
        success_count = 0
        for name, agent in self.agents.items():
            if agent.initialize():
                success_count += 1
                logger.info(f"✓ {name} agent ready")
            else:
                logger.error(f"✗ {name} agent failed to initialize")
        
        total_agents = len(self.agents)
        logger.info(f"Agent initialization complete: {success_count}/{total_agents} successful")
        
        return success_count == total_agents
    
    async def process_frame_collaborative(self, frame: np.ndarray) -> FrameAnalysis:
        """Process frame using all agents collaboratively"""
        self.frame_counter += 1
        start_time = time.time()
        
        # Phase 1: Independent agent processing
        agent_results = {}
        
        # Object detection (runs first as others may use its results)
        obj_result = self.agents["object_detection"].process_frame(frame, self.frame_counter)
        agent_results["object_detection"] = obj_result
        
        # Motion analysis (can run in parallel)
        motion_result = self.agents["motion_analysis"].process_frame(frame, self.frame_counter)
        agent_results["motion_analysis"] = motion_result
        
        # Anomaly detection (uses context from other agents)
        anomaly_context = {
            "object_detection": obj_result,
            "motion_analysis": motion_result
        }
        anomaly_result = self.agents["anomaly_detection"].process_frame(
            frame, self.frame_counter, anomaly_context
        )
        agent_results["anomaly_detection"] = anomaly_result
        
        # Phase 2: Collaborative analysis and consensus
        collaborative_results = self._perform_collaborative_analysis(agent_results)
        
        # Phase 3: Generate final analysis
        total_processing_time = (time.time() - start_time) * 1000
        
        analysis = FrameAnalysis(
            frame_id=self.frame_counter,
            timestamp=datetime.now(),
            detections=obj_result.get("detections", []),
            alerts=anomaly_result.get("alerts", []),
            agent_results=agent_results,
            processing_time=total_processing_time
        )
        
        # Update statistics
        self._update_statistics(total_processing_time)
        
        return analysis
    
    def _perform_collaborative_analysis(self, agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """Perform collaborative analysis using results from all agents"""
        collaborative = {
            "confidence_score": 0.0,
            "consensus_alerts": [],
            "cross_validated_detections": []
        }
        
        # Cross-validate detections using motion analysis
        obj_detections = agent_results.get("object_detection", {}).get("detections", [])
        motion_regions = agent_results.get("motion_analysis", {}).get("motion_patterns", {}).get("motion_regions", [])
        
        # Correlate detections with motion
        for detection in obj_detections:
            detection_bbox = detection.bbox
            has_motion_correlation = self._check_motion_correlation(detection_bbox, motion_regions)
            
            if has_motion_correlation:
                # Increase confidence for detections correlated with motion
                enhanced_detection = detection
                enhanced_detection.confidence = min(1.0, detection.confidence + 0.1)
                collaborative["cross_validated_detections"].append(enhanced_detection)
            else:
                collaborative["cross_validated_detections"].append(detection)
        
        # Calculate overall confidence based on agent agreement
        confidence_factors = []
        
        if agent_results.get("object_detection", {}).get("detections"):
            confidence_factors.append(0.3)  # Object detection contribution
        
        if agent_results.get("motion_analysis", {}).get("has_significant_motion"):
            confidence_factors.append(0.3)  # Motion analysis contribution
        
        if agent_results.get("anomaly_detection", {}).get("anomaly_score", 0) < 0.5:
            confidence_factors.append(0.4)  # Normal behavior contribution
        
        collaborative["confidence_score"] = sum(confidence_factors)
        
        return collaborative
    
    def _check_motion_correlation(self, detection_bbox: Tuple[int, int, int, int], 
                                motion_regions: List[Dict]) -> bool:
        """Check if detection correlates with motion regions"""
        det_x, det_y, det_w, det_h = detection_bbox
        
        for region in motion_regions:
            mot_x, mot_y, mot_w, mot_h = region["bbox"]
            
            # Calculate overlap using Intersection over Union (IoU)
            overlap_area = max(0, min(det_x + det_w, mot_x + mot_w) - max(det_x, mot_x)) * \
                          max(0, min(det_y + det_h, mot_y + mot_h) - max(det_y, mot_y))
            
            det_area = det_w * det_h
            mot_area = mot_w * mot_h
            union_area = det_area + mot_area - overlap_area
            
            if union_area > 0:
                iou = overlap_area / union_area
                if iou > 0.3:  # Threshold for correlation
                    return True
        
        return False
    
    def _update_statistics(self, processing_time: float):
        """Update processing statistics"""
        self.processing_stats["total_frames"] += 1
        self.processing_stats["total_processing_time"] += processing_time
        
        # Update individual agent statistics
        for name, agent in self.agents.items():
            if name not in self.processing_stats["agent_stats"]:
                self.processing_stats["agent_stats"][name] = {
                    "avg_processing_time": 0.0,
                    "total_calls": 0
                }
            
            agent_stats = self.processing_stats["agent_stats"][name]
            agent_stats["avg_processing_time"] = agent.get_average_processing_time()
            agent_stats["total_calls"] = len(agent.processing_times)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        if self.processing_stats["total_frames"] > 0:
            avg_total_time = (self.processing_stats["total_processing_time"] / 
                            self.processing_stats["total_frames"])
        else:
            avg_total_time = 0.0
        
        return {
            "total_frames_processed": self.processing_stats["total_frames"],
            "average_processing_time": avg_total_time,
            "frames_per_second": 1000.0 / avg_total_time if avg_total_time > 0 else 0.0,
            "agent_performance": self.processing_stats["agent_stats"]
        }

# ===== VIDEO PROCESSING PIPELINE =====

class VideoProcessor:
    """Main video processing pipeline"""
    
    def __init__(self, max_buffer_size: int = 30):
        self.coordinator = AgentCoordinator()
        self.frame_buffer = Queue(maxsize=max_buffer_size)
        self.results_buffer = Queue(maxsize=100)
        self.is_running = False
        self.processing_thread = None
        
    def initialize(self) -> bool:
        """Initialize the video processor"""
        logger.info("Initializing Video Processor...")
        return self.coordinator.initialize_all_agents()
    
    def start_processing(self, video_source: str = 0):
        """Start video processing from source"""
        if not self.coordinator.agents:
            logger.error("Agents not initialized. Call initialize() first.")
            return False
        
        self.is_running = True
        self.processing_thread = threading.Thread(
            target=self._process_video_stream, 
            args=(video_source,)
        )
        self.processing_thread.start()
        logger.info(f"Started video processing from source: {video_source}")
        return True
    
    def stop_processing(self):
        """Stop video processing"""
        self.is_running = False
        if self.processing_thread:
            self.processing_thread.join(timeout=5.0)
        logger.info("Video processing stopped")
    
    def _process_video_stream(self, video_source):
        """Main video processing loop"""
        cap = cv2.VideoCapture(video_source)
        
        if not cap.isOpened():
            logger.error(f"Failed to open video source: {video_source}")
            return
        
        logger.info("Video stream opened successfully")
        
        try:
            while self.is_running and cap.isOpened():
                ret, frame = cap.read()
                
                if not ret:
                    logger.warning("Failed to read frame from video source")
                    break
                
                # Process frame asynchronously
                try:
                    # Create event loop for async processing
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    analysis = loop.run_until_complete(
                        self.coordinator.process_frame_collaborative(frame)
                    )
                    
                    # Store results
                    if not self.results_buffer.full():
                        self.results_buffer.put({
                            "frame": frame.copy(),
                            "analysis": analysis
                        })
                    
                    # Display results (for debugging)
                    self._display_results(frame, analysis)
                    
                    loop.close()
                    
                except Exception as e:
                    logger.error(f"Error processing frame: {e}")
                    continue
                
                # Control frame rate (roughly 30 FPS)
                time.sleep(0.033)
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
            logger.info("Video capture released")
    
    def _display_results(self, frame: np.ndarray, analysis: FrameAnalysis):
        """Display results on the frame for debugging"""
        display_frame = frame.copy()
        
        # Draw detections
        for detection in analysis.detections:
            x, y, w, h = detection.bbox
            cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            label = f"{detection.class_name}: {detection.confidence:.2f}"
            cv2.putText(display_frame, label, (x, y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        # Draw alerts
        if analysis.alerts:
            alert_text = f"ALERTS: {len(analysis.alerts)}"
            cv2.putText(display_frame, alert_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Show processing info
        info_text = f"Frame: {analysis.frame_id} | Time: {analysis.processing_time:.1f}ms"
        cv2.putText(display_frame, info_text, (10, display_frame.shape[0] - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        cv2.imshow("Real-Time Video Analytics", display_frame)
        
        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            self.is_running = False
    
    def get_latest_results(self, count: int = 10) -> List[Dict]:
        """Get latest analysis results"""
        results = []
        temp_queue = Queue()
        
        # Extract results while preserving queue
        while not self.results_buffer.empty() and len(results) < count:
            item = self.results_buffer.get()
            results.append(item)
            temp_queue.put(item)
        
        # Put items back
        while not temp_queue.empty():
            self.results_buffer.put(temp_queue.get())
        
        return results[::-1]  # Return most recent first

# ===== MAIN APPLICATION =====

def main():
    """Main application entry point"""
    logger.info("=== Real-Time Video Analytics with Collaborative Agents ===")
    
    # Create video processor
    processor = VideoProcessor()
    
    # Initialize system
    if not processor.initialize():
        logger.error("Failed to initialize video processor")
        return
    
    logger.info("System initialized successfully!")
    
    try:
        # Start processing (0 = default camera, or specify video file path)
        video_source = 0  # Change to video file path if needed
        
        if processor.start_processing(video_source):
            logger.info("Video processing started. Press 'q' in video window to quit.")
            
            # Keep main thread alive and show periodic stats
            while processor.is_running:
                time.sleep(5)  # Update every 5 seconds
                
                # Display performance statistics
                stats = processor.coordinator.get_performance_stats()
                logger.info(f"Performance: {stats['frames_per_second']:.1f} FPS, "
                          f"Avg processing time: {stats['average_processing_time']:.1f}ms")
                
                # Display recent results summary
                recent_results = processor.get_latest_results(5)
                if recent_results:
                    total_detections = sum(len(r['analysis'].detections) for r in recent_results)
                    total_alerts = sum(len(r['analysis'].alerts) for r in recent_results)
                    logger.info(f"Recent activity: {total_detections} detections, {total_alerts} alerts")
        
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    
    finally:
        # Cleanup
        processor.stop_processing()
        logger.info("Application shutdown complete")

if __name__ == "__main__":
    main()
