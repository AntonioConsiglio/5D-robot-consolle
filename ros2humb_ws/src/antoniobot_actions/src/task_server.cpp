#include <rclcpp/rclcpp.hpp>
#include <rclcpp_action/rclcpp_action.hpp>
#include <antoniobot_msgs/action/target_goal.hpp>
#include <moveit/move_group_interface/move_group_interface.h>
#include <moveit_msgs/msg/constraints.hpp>
#include <moveit_msgs/msg/orientation_constraint.hpp>

#include <memory>

#include <rclcpp_components/register_node_macro.hpp>
#include <vector>

#include <thread>

using namespace std::placeholders;

namespace antoniobot_actions
{
class TaskServer : public rclcpp::Node
{
public:
    explicit TaskServer(const rclcpp::NodeOptions& options = rclcpp::NodeOptions()) : Node("task_server",options)
    {
        actionServer_ = rclcpp_action::create_server<antoniobot_msgs::action::TargetGoal>(
        this,"task_server",
        std::bind(&TaskServer::goalCallback,this,_1,_2),
        std::bind(&TaskServer::cancelCallback,this,_1),
        std::bind(&TaskServer::acceptedCallback,this,_1));
    
    RCLCPP_INFO(rclcpp::get_logger("rclcpp"),"Starting the TargetGoal Action Server!");
    };


private:
    rclcpp_action::Server<antoniobot_msgs::action::TargetGoal>::SharedPtr actionServer_;
    rclcpp_action::GoalResponse goalCallback(const rclcpp_action::GoalUUID uuid, std::shared_ptr<const antoniobot_msgs::action::TargetGoal::Goal> goal)
    {
        RCLCPP_INFO_STREAM(get_logger(),"Received goal request with x: "<<goal->x<<" y: "<<goal->y <<" z: "<<goal->z );
        return rclcpp_action::GoalResponse::ACCEPT_AND_EXECUTE;
    }

    void acceptedCallback(const std::shared_ptr<rclcpp_action::ServerGoalHandle<antoniobot_msgs::action::TargetGoal>> goal_handle)
    {
        std::thread(std::bind(&TaskServer::execute,this,_1),goal_handle).detach();
    }

    void execute(const std::shared_ptr<rclcpp_action::ServerGoalHandle<antoniobot_msgs::action::TargetGoal>> goal_handle)
    {
        RCLCPP_INFO(get_logger(),"Executing goal!");
        
        auto arm_move_group = moveit::planning_interface::MoveGroupInterface(shared_from_this(),"arm");
        //geometry_msgs::msg::Quaternion currPose = arm_move_group.getCurrentPose().pose.orientation;
        // geometry_msgs::msg::Quaternion currPose;
        // currPose.set__x(0);
        // currPose.set__y(0);
        // currPose.set__z(0);
        // currPose.set__w(1);
        // RCLCPP_INFO_STREAM(get_logger(),"Current orientation of Virtual_Yaw_Link: " <<"x: "<< currPose.x <<" y: " <<currPose.y <<" z: " <<currPose.z <<" w: " <<currPose.w );
        // //auto gripper_move_group = moveit::planning_interface::MoveGroupInterface(shared_from_this(),"gripper");
        // // arm_move_group.setPoseReferenceFrame("base_link");
        // //arm_move_group.setEndEffectorLink("virtual_yaw_link");

        // moveit_msgs::msg::OrientationConstraint orientation_constraint;
        // orientation_constraint.header.frame_id  = arm_move_group.getPoseReferenceFrame();
        // orientation_constraint.set__link_name("virtual_yaw_link");
        // orientation_constraint.orientation = currPose;
        // orientation_constraint.absolute_x_axis_tolerance = 0.4;
        // orientation_constraint.absolute_y_axis_tolerance = 0.4;
        // orientation_constraint.absolute_z_axis_tolerance = 0.4;
        // orientation_constraint.weight = 1.0;
        
        // moveit_msgs::msg::Constraints orientation_constraints;
        // orientation_constraints.orientation_constraints.emplace_back(orientation_constraint);
        
        // arm_move_group.setPathConstraints(orientation_constraints);

        arm_move_group.setPlanningTime(10.0);
        std::vector<double> arm_joint_goal {0.0,0.0,0.0};
        //std::vector<double> gripper_joint_goal;

        arm_joint_goal[0] = goal_handle->get_goal()->x;
        arm_joint_goal[1] = goal_handle->get_goal()->y;
        arm_joint_goal[2] = goal_handle->get_goal()->z;

        bool arm_within_bounds = arm_move_group.setPositionTarget(arm_joint_goal[0],
                                                                  arm_joint_goal[1],
                                                                  arm_joint_goal[2],
                                                                  "virtual_yaw_link");
                                                                  
        if(!arm_within_bounds)
        {
            RCLCPP_WARN(rclcpp::get_logger("rclcpp"),"Target joint position were outside the limits");
            return;
        }

        moveit::planning_interface::MoveGroupInterface::Plan arm_plan;
        //moveit::planning_interface::MoveGroupInterface::Plan gripper_plan;

        bool arm_plan_success = arm_move_group.plan(arm_plan) == moveit::core::MoveItErrorCode::SUCCESS;
        //bool gripper_plan_success = gripper_move_group.plan(gripper_plan) == moveit::core::MoveItErrorCode::SUCCESS;

        if(arm_plan_success) // && gripper_plan_success)
        {   
            
            RCLCPP_INFO(rclcpp::get_logger("rclcpp"),"Planner succed, moving the arm and gripper");
            arm_move_group.move();
            //gripper_move_group.move();
        }
        else
        {
            RCLCPP_ERROR(rclcpp::get_logger("rclcpp"),"One or more planners failed!");
            return;
        }

        auto result = std::make_shared<antoniobot_msgs::action::TargetGoal::Result>();
        result->success = true;
        goal_handle->succeed(result);
        RCLCPP_INFO(rclcpp::get_logger("rclcpp"), "Goal succeded!");
    }

    rclcpp_action::CancelResponse cancelCallback(const std::shared_ptr<rclcpp_action::ServerGoalHandle<antoniobot_msgs::action::TargetGoal>> goal_handle)
    {
        RCLCPP_INFO(get_logger(),"Received request to cancel the goal!");
        auto arm_move_group = moveit::planning_interface::MoveGroupInterface(shared_from_this(),"arm");
        //auto gripper_move_group = moveit::planning_interface::MoveGroupInterface(shared_from_this(),"gripper");

        arm_move_group.stop();
        //gripper_move_group.stop();

        return rclcpp_action::CancelResponse::ACCEPT;
    }

};

}

RCLCPP_COMPONENTS_REGISTER_NODE(antoniobot_actions::TaskServer)