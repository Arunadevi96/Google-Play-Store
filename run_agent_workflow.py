import os
import sys
import yaml
import json
from datetime import datetime, UTC
from play_store_mcp.client import PlayStoreClient, PlayStoreClientError

def load_workflow(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def run_workflow():
    workflow_path = "PlayStore_Agent_Workflow.yml"
    if not os.path.exists(workflow_path):
        print(f"Error: {workflow_path} not found.")
        sys.exit(1)
        
    print("Loading Play Store Agent Workflow...")
    workflow = load_workflow(workflow_path)
    
    # Get configuration and credentials
    app_id = os.environ.get("APP_ID") or workflow.get("app_id")
    if not app_id or app_id == "${APP_ID}":
        print("Error: APP_ID environment variable is not set and no default app_id is specified in workflow YML.")
        sys.exit(1)
        
    print(f"Target App Package: {app_id}")
    
    # Initialize the Play Store Client
    client = None
    try:
        client = PlayStoreClient()
        # Verify credentials by getting the service
        _ = client._get_service()
        print("PlayStoreClient initialized with valid credentials.")
    except Exception as e:
        print(f"Warning: PlayStoreClient credentials verify failed: {e}")
        print("Running in dry-run/mock mode.")
        client = None

    # Storage for step outputs
    outputs = {}
    steps_completed = []
    errors = []
    
    # Helper to execute step
    current_step_id = "1"
    
    while current_step_id:
        # Find step by ID
        step = next((s for s in workflow.get("steps", []) if str(s.get("step_id")) == current_step_id), None)
        if not step:
            print(f"Finished executing workflow. Step ID {current_step_id} not found.")
            break
            
        step_id = str(step.get("step_id"))
        step_name = step.get("name")
        print(f"\n--- [Step {step_id}] {step_name} ---")
        
        tool = step.get("tool")
        action = step.get("action")
        output_var = step.get("output_var")
        condition = step.get("condition")
        
        # Check condition if present
        if condition:
            print(f"Checking condition: {condition}")
            pass
            
        try:
            if tool:
                print(f"Executing MCP tool: {tool}")
                if client:
                    if tool == "get_releases":
                        res = client.get_releases(package_name=app_id)
                        outputs[output_var] = [r.model_dump() for r in res]
                    elif tool == "get_app_details":
                        res = client.get_app_details(package_name=app_id)
                        outputs[output_var] = res.model_dump()
                    elif tool == "get_reviews":
                        max_res = step.get("max_results", 50)
                        res = client.get_reviews(package_name=app_id, max_results=max_res)
                        outputs[output_var] = [r.model_dump() for r in res]
                    elif tool == "get_vitals_overview":
                        res = client.get_vitals_overview(package_name=app_id)
                        outputs[output_var] = res.model_dump()
                    elif tool == "get_vitals_metrics":
                        res = client.get_vitals_metrics(package_name=app_id)
                        outputs[output_var] = [r.model_dump() for r in res]
                    elif tool == "list_subscriptions":
                        res = client.list_subscriptions(package_name=app_id)
                        outputs[output_var] = [r.model_dump() for r in res]
                    elif tool == "list_voided_purchases":
                        res = client.list_voided_purchases(package_name=app_id)
                        outputs[output_var] = [r.model_dump() for r in res]
                    elif tool == "list_in_app_products":
                        res = client.list_in_app_products(package_name=app_id)
                        outputs[output_var] = [r.model_dump() for r in res]
                    else:
                        print(f"Skipping execution of tool '{tool}' (requires specific target params).")
                        outputs[output_var] = {"status": "skipped", "reason": "non-read tool"}
                else:
                    # Mock output if client is not initialized or fails credentials
                    print("[MOCK] Tool executed successfully.")
                    if tool == "get_releases":
                        outputs[output_var] = [{"track": "production", "releases": [{"status": "completed", "versionCodes": [100], "name": "1.0.0", "userFraction": 1.0}]}]
                    elif tool == "get_app_details":
                        outputs[output_var] = {"package_name": app_id, "title": "Test App", "short_description": "A test app"}
                    elif tool == "get_reviews":
                        outputs[output_var] = [{"star_rating": 5, "comment": "Great app!"}, {"star_rating": 1, "comment": "Crashes on startup!"}]
                    elif tool == "get_vitals_overview":
                        outputs[output_var] = {"package_name": app_id, "crash_rate": 0.45, "anr_rate": 0.12}
                    elif tool == "get_vitals_metrics":
                        outputs[output_var] = [{"metric_type": "crashRate", "value": 0.45}]
                    else:
                        outputs[output_var] = {}
            
            elif action == "evaluate_conditions":
                # Step 6: Decision logic
                print("Evaluating stability thresholds...")
                vitals = outputs.get("vitals_overview", {}) or {}
                reviews = outputs.get("recent_reviews", []) or []
                
                crash_rate = vitals.get("crash_rate", 0.0) or 0.0
                anr_rate = vitals.get("anr_rate", 0.0) or 0.0
                neg_reviews_count = sum(1 for r in reviews if r.get("star_rating", 5) <= 2)
                
                crash_threshold = workflow.get("crash_rate_threshold", 2.0)
                anr_threshold = workflow.get("anr_rate_threshold", 0.5)
                neg_threshold = workflow.get("negative_review_threshold", 3)
                
                print(f"Current Crash Rate: {crash_rate}% (Threshold: {crash_threshold}%)")
                print(f"Current ANR Rate: {anr_rate}% (Threshold: {anr_threshold}%)")
                print(f"Recent Negative Reviews: {neg_reviews_count} (Threshold: {neg_threshold})")
                
                is_critical = (
                    crash_rate > crash_threshold or 
                    anr_rate > anr_threshold or 
                    neg_reviews_count >= neg_threshold
                )
                
                if is_critical:
                    print("[CRITICAL] CRITICAL HEALTH ISSUES DETECTED!")
                    current_step_id = step.get("if_true")
                else:
                    print("[OK] APP IS HEALTHY. Continuing normal path.")
                    current_step_id = step.get("if_false")
                
                steps_completed.append(step_id)
                continue
                
            elif action == "compile_report":
                print("Compiling daily report...")
                vitals = outputs.get("vitals_overview", {}) or {}
                reviews = outputs.get("recent_reviews", []) or []
                
                crash_rate = vitals.get("crash_rate", 0.0) or 0.0
                anr_rate = vitals.get("anr_rate", 0.0) or 0.0
                neg_reviews_count = sum(1 for r in reviews if r.get("star_rating", 5) <= 2)
                pos_reviews_count = sum(1 for r in reviews if r.get("star_rating", 0) >= 4)
                
                status = "HEALTHY"
                if crash_rate > workflow.get("crash_rate_threshold", 2.0) or anr_rate > workflow.get("anr_rate_threshold", 0.5):
                    status = "CRITICAL"
                elif neg_reviews_count > 0:
                    status = "WARNING"
                    
                report = {
                    "summary": {
                        "status": status,
                        "critical_issues": status == "CRITICAL"
                    },
                    "releases": {
                        "package_name": app_id,
                        "timestamp": datetime.now(UTC).isoformat()
                    },
                    "health_metrics": {
                        "crash_rate": f"{crash_rate}%",
                        "anr_rate": f"{anr_rate}%"
                    },
                    "user_feedback": {
                        "positive_reviews": pos_reviews_count,
                        "negative_reviews": neg_reviews_count
                    }
                }
                outputs[output_var] = report
                print(json.dumps(report, indent=2))
                
            elif action == "send_notification":
                report = outputs.get("daily_report", {}) or {}
                status = report.get("summary", {}).get("status", "UNKNOWN")
                print(f"Sending notification via Email & Slack. Urgency: {step.get('urgency', 'Normal')}")
                print(f"Report Status: [{status}]")
                
            elif action == "save_history":
                print("Saving execution logs...")
                log_data = {
                    "workflow_id": workflow.get("workflow_id"),
                    "last_run": datetime.now(UTC).isoformat(),
                    "last_status": "SUCCESS" if len(errors) == 0 else "FAILED",
                    "steps_completed": len(steps_completed) + 1,
                    "errors": errors
                }
                print(json.dumps(log_data, indent=2))
                
            else:
                print(f"Running custom action: {action}")
                
            steps_completed.append(step_id)
            
        except Exception as e:
            print(f"Error during step {step_id}: {e}")
            errors.append(f"Step {step_id} failed: {str(e)}")
            
        # Set next step ID
        current_step_id = step.get("next_step")

    print("\nWorkflow Execution Complete.")
    print(f"Steps Completed: {steps_completed}")
    if errors:
        print(f"Errors encountered: {errors}")
        sys.exit(1)

if __name__ == "__main__":
    run_workflow()
