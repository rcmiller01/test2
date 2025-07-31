#!/usr/bin/env python3
"""
Reflection Agent v0.1 - Emotional Drift Detection and Anchor Insight Generation

This agent scans emotional reflection logs to detect drift from seed emotions and 
generates structured insights for the Anchor AI system to respond to.

Author: Dolphin AI System
Date: July 31, 2025
"""

import os
import json
import datetime
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Any

# === Config Paths ===
REFLECTION_LOG_DIR = 'reflection_logs'
SEED_EMOTION_PATH = 'config/seed_emotions.json'
ANCHOR_INSIGHT_PATH = 'emotion_logs/anchor_insights.json'

# === Parameters ===
NUM_LOG_LINES = 50  # How many recent reflections to scan

def load_seed_emotions(path=SEED_EMOTION_PATH):
    """Load seed emotions from configuration file"""
    try:
        # Handle relative paths from the script location
        if not os.path.isabs(path):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(script_dir, '..', path)
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # Handle both flat structure and nested "protected_emotions" structure
            if "protected_emotions" in data:
                emotions = data["protected_emotions"]
            else:
                emotions = data
                
            print(f"[Reflection Agent] Loaded {len(emotions)} seed emotions from {path}")
            return emotions
    except FileNotFoundError:
        print(f"[Reflection Agent] Warning: Seed emotions file not found at {path}")
        return {}
    except json.JSONDecodeError as e:
        print(f"[Reflection Agent] Error parsing seed emotions JSON: {e}")
        return {}
    except Exception as e:
        print(f"[Reflection Agent] Error loading seed emotions: {e}")
        return {}

def get_recent_reflection_entries(log_dir=REFLECTION_LOG_DIR, max_lines=NUM_LOG_LINES):
    """Extract recent reflection entries from log files"""
    entries = []
    
    # Handle relative paths
    if not os.path.isabs(log_dir):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        log_dir = os.path.join(script_dir, '..', log_dir)
    
    if not os.path.exists(log_dir):
        print(f"[Reflection Agent] Warning: Reflection log directory not found at {log_dir}")
        print(f"[Reflection Agent] Creating directory: {log_dir}")
        os.makedirs(log_dir, exist_ok=True)
        return entries
    
    log_files = [f for f in os.listdir(log_dir) if f.endswith('.jsonl')]
    print(f"[Reflection Agent] Found {len(log_files)} log files in {log_dir}")
    
    for file in log_files:
        path = os.path.join(log_dir, file)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()[-max_lines:]
                for line in lines:
                    try:
                        entry = json.loads(line.strip())
                        entries.append(entry)
                    except json.JSONDecodeError:
                        continue  # Skip malformed lines
        except Exception as e:
            print(f"[Reflection Agent] Error reading {file}: {e}")
            continue
    
    print(f"[Reflection Agent] Loaded {len(entries)} reflection entries")
    return entries

def analyze_reflections(entries, seed_emotions):
    """Analyze reflection entries for emotional drift"""
    def create_drift_entry():
        return {"mentions": 0, "violations": 0, "examples": []}
    
    drift_report = defaultdict(create_drift_entry)
    
    if not entries:
        print("[Reflection Agent] No entries to analyze")
        return drift_report
    
    if not seed_emotions:
        print("[Reflection Agent] No seed emotions to check against")
        return drift_report
    
    for entry in entries:
        prompt = entry.get('prompt', '').lower()
        response = entry.get('response', '').lower()
        score = entry.get('score', 0)
        
        # Check each seed emotion for presence and quality
        for key, value in seed_emotions.items():
            keyword = key.lower()
            
            # Check if this emotion is mentioned in prompt or response
            if keyword in prompt or keyword in response:
                drift_report[key]["mentions"] += 1
                
                # Threshold for shallow or misaligned emotional presence
                if score < 0.6:  
                    drift_report[key]["violations"] += 1
                    drift_report[key]["examples"].append({
                        "prompt": prompt[:200],  # Truncate for readability
                        "response": response[:200],
                        "score": score,
                        "timestamp": entry.get('timestamp', 'unknown')
                    })
    
    # Report findings
    total_violations = sum(data["violations"] for data in drift_report.values())
    total_mentions = sum(data["mentions"] for data in drift_report.values())
    
    print(f"[Reflection Agent] Analysis complete: {total_mentions} mentions, {total_violations} violations")
    
    return drift_report

def write_anchor_insight(report, output_path=ANCHOR_INSIGHT_PATH):
    """Write structured anchor insights for the Anchor AI system"""
    
    # Handle relative paths
    if not os.path.isabs(output_path):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, '..', output_path)
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    out = {
        "timestamp": datetime.datetime.now().isoformat(),
        "analysis_version": "0.1",
        "summary": {},
        "overall_health": "healthy"  # Will be updated based on drift scores
    }
    
    total_drift = 0
    emotion_count = 0
    
    for key, data in report.items():
        mentions = data["mentions"]
        violations = data["violations"]
        
        # Calculate drift score (0 = perfect, 1 = complete drift)
        if mentions > 0:
            drift_score = violations / mentions
        else:
            drift_score = 0
        
        total_drift += drift_score
        emotion_count += 1 if mentions > 0 else 0
        
        out["summary"][key] = {
            "mentions": mentions,
            "violations": violations,
            "drift_score": round(drift_score, 3),
            "examples": data["examples"][:3]  # Trim examples for readability
        }
    
    # Calculate overall health
    if emotion_count > 0:
        avg_drift = total_drift / emotion_count
        if avg_drift < 0.2:
            out["overall_health"] = "healthy"
        elif avg_drift < 0.5:
            out["overall_health"] = "concerning"
        else:
            out["overall_health"] = "critical"
    
    out["statistics"] = {
        "emotions_analyzed": emotion_count,
        "average_drift_score": round(total_drift / max(emotion_count, 1), 3),
        "high_drift_emotions": [k for k, v in out["summary"].items() if v["drift_score"] > 0.5]
    }
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(out, f, indent=2, ensure_ascii=False)
        
        print(f"[Reflection Agent] Anchor insight written to {output_path}")
        print(f"[Reflection Agent] Overall health: {out['overall_health']}")
        print(f"[Reflection Agent] Average drift score: {out['statistics']['average_drift_score']}")
        
        if out["statistics"]["high_drift_emotions"]:
            print(f"[Reflection Agent] High drift emotions detected: {', '.join(out['statistics']['high_drift_emotions'])}")
        
    except Exception as e:
        print(f"[Reflection Agent] Error writing anchor insights: {e}")

def run_reflection_pass():
    """Main function to run a complete reflection analysis pass"""
    print("[Reflection Agent] Starting emotional reflection analysis...")
    print(f"[Reflection Agent] Timestamp: {datetime.datetime.now().isoformat()}")
    
    try:
        # Load configuration and data
        seeds = load_seed_emotions()
        entries = get_recent_reflection_entries()
        
        # Perform analysis
        report = analyze_reflections(entries, seeds)
        
        # Generate insights
        write_anchor_insight(report)
        
        print("[Reflection Agent] Reflection pass completed successfully")
        
    except Exception as e:
        print(f"[Reflection Agent] Error during reflection pass: {e}")
        import traceback
        traceback.print_exc()

def create_sample_seed_emotions():
    """Create a sample seed emotions configuration file for testing"""
    sample_seeds = {
        "faith": {
            "description": "Deep spiritual trust and belief",
            "keywords": ["faith", "belief", "trust", "spiritual"],
            "importance": "high"
        },
        "love": {
            "description": "Unconditional love and compassion",
            "keywords": ["love", "compassion", "care", "affection"],
            "importance": "critical"
        },
        "hope": {
            "description": "Optimism and positive outlook",
            "keywords": ["hope", "optimism", "future", "possibility"],
            "importance": "high"
        },
        "wisdom": {
            "description": "Deep understanding and insight",
            "keywords": ["wisdom", "understanding", "insight", "knowledge"],
            "importance": "medium"
        },
        "joy": {
            "description": "Authentic happiness and delight",
            "keywords": ["joy", "happiness", "delight", "celebration"],
            "importance": "high"
        }
    }
    
    config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config')
    os.makedirs(config_dir, exist_ok=True)
    
    config_path = os.path.join(config_dir, 'seed_emotions.json')
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(sample_seeds, f, indent=2, ensure_ascii=False)
    
    print(f"[Reflection Agent] Sample seed emotions created at {config_path}")

if __name__ == "__main__":
    print("🧠 Reflection Agent v0.1 - Emotional Drift Detection")
    print("=" * 60)
    
    # Check if seed emotions exist, create sample if not
    seed_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', SEED_EMOTION_PATH)
    if not os.path.exists(seed_path):
        print("[Reflection Agent] Seed emotions not found, creating sample configuration...")
        create_sample_seed_emotions()
    
    # Run the reflection analysis
    run_reflection_pass()
    
    print("=" * 60)
    print("🔜 Next Steps:")
    print("- Hook this into a cron job or run after every emotion loop")
    print("- Teach Anchor AI to read the insights and respond to drift")
    print("- Add voice reflection capabilities")
    print("- Monitor anchor_insights.json for realignment triggers")
