#!/usr/bin/env python3
"""
Demo script showing the new workflow:
1. Create local plan (no API call)
2. Push plan to API when user chooses
3. Execute steps using API
"""

def demo_workflow():
    """Demonstrate the new workflow"""
    print("🚀 Demo: New Planner API Workflow")
    print("=" * 50)

    # Step 1: Create local plan (no API call)
    print("\n📝 Step 1: Create Local Plan")
    print("✅ Local plan created!")
    print("Task: Bật đèn và điều hòa trong phòng khách")
    print("Room: phòng khách")
    print("Priority: high")
    print("Total Steps: 3")
    print("Steps:")
    print("  1. Bật đèn phòng khách")
    print("  2. Bật điều hòa ở nhiệt độ 25°C")
    print("  3. Kiểm tra trạng thái các thiết bị")
    print("\n📝 Use 'push_plan_to_api' tool to execute this plan, or create a custom plan.")

    # Step 2: User chooses plan and pushes to API
    print("\n📤 Step 2: Push Plan to API")
    print("✅ Plan pushed to API successfully!")
    print("Plan ID: demo-plan-id")
    print("Title: Plan: Bật đèn và điều hòa")
    print("Room: phòng khách")
    print("Tasks (3):")
    print("  1. Bật đèn phòng khách (ID: task-1)")
    print("  2. Bật điều hòa ở nhiệt độ 25°C (ID: task-2)")
    print("  3. Kiểm tra trạng thái các thiết bị (ID: task-3)")
    print("\n🚀 Ready for execution! Use 'execute_step' tool to run tasks.")

    # Step 3: Execute steps
    print("\n🔄 Step 3: Execute Steps")
    print("✅ Step completed successfully!")
    print("Plan ID: demo-plan-id")
    print("Step ID: task-1")
    print("Command: bật đèn")
    print("Attempts: 1")
    print("Service: Connected to Temp API")

    print("\n✅ Workflow Demo Complete!")
    print("\n📖 New Workflow Summary:")
    print("   1. create_plan → Tạo plan local, show options cho user chọn")
    print("   2. push_plan_to_api → Push plan đã chọn lên API")
    print("   3. execute_step → Execute từng step, update status qua API")
    print("\n🔧 Tools available:")
    print("   - create_plan: Tạo plan local")
    print("   - push_plan_to_api: Push plan lên API")
    print("   - execute_step: Execute step và update status")

if __name__ == "__main__":
    demo_workflow()