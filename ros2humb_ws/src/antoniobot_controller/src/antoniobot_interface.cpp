#include "antoniobot_controller/antoniobot_interface.hpp"
#include <hardware_interface/types/hardware_interface_type_values.hpp>

#include <pluginlib/class_list_macros.hpp>
#include <thread>
#include <chrono>

namespace antoniobot_controller
{
    AntoniobotInterface::AntoniobotInterface()
    {

    }

    AntoniobotInterface::~AntoniobotInterface()
    {
        if(arduino_socket.IsOpen())
        {
            try
            {
                arduino_socket.Close();
            }
            catch(...)
            {
                RCLCPP_FATAL_STREAM(rclcpp::get_logger("AntoniobotInterface"),"Something went wrong while closing the connection with port " << port_);
            }
        }
    }

    CallbackReturn AntoniobotInterface::on_init(const hardware_interface::HardwareInfo & hardware_info)
    {
        CallbackReturn result =  hardware_interface::SystemInterface::on_init(hardware_info);
        if(result != CallbackReturn::SUCCESS){
            return result;
        }
        try
        {
            RCLCPP_INFO_STREAM(rclcpp::get_logger("AntoniobotInterface"),"On init function...PORT: " << info_.hardware_parameters.at("port"));
            port_ = info_.hardware_parameters.at("port");
        }
        catch(const std::out_of_range &e)
        {
            RCLCPP_FATAL_STREAM(rclcpp::get_logger("AntoniobotInterface"),"port value doesn't assigned! " <<  e.what());
            return CallbackReturn::FAILURE;
        }
        //reserve space for vectors
        position_commands_.reserve(info_.joints.size());
        position_states_.reserve(info_.joints.size());
        previous_position_commands_.reserve(info_.joints.size());
        return CallbackReturn::SUCCESS;
    }

    std::vector<hardware_interface::StateInterface> AntoniobotInterface::export_state_interfaces()
    {
        std::vector<hardware_interface::StateInterface> state_interfaces;
        for(size_t i = 0; i < info_.joints.size(); i++ )
        {
            state_interfaces.emplace_back(hardware_interface::StateInterface(info_.joints[i].name,hardware_interface::HW_IF_POSITION, &position_states_[i]));
        } 
        return state_interfaces;
    }

    std::vector<hardware_interface::CommandInterface> AntoniobotInterface::export_command_interfaces()
    {
        std::vector<hardware_interface::CommandInterface> command_interfaces;
        for(size_t i = 0; i < info_.joints.size(); i++ )
        {
            command_interfaces.emplace_back(hardware_interface::CommandInterface(info_.joints[i].name,hardware_interface::HW_IF_POSITION, &position_commands_[i]));
        } 
        return command_interfaces;
    }

    CallbackReturn AntoniobotInterface::on_activate(const rclcpp_lifecycle::State & previous_state)
    {
        RCLCPP_INFO(rclcpp::get_logger("AntoniobotInterface"),"Starting the robot hardware...");
        position_commands_ = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
        previous_position_commands_ =  {0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
        position_states_ =  {0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
        send_to_arduino = false;
        try
        {
            arduino_socket.Open(port_);
            arduino_socket.SetBaudRate(LibSerial::BaudRate::BAUD_115200);
        }
        catch(...)
        {
            RCLCPP_FATAL_STREAM(rclcpp::get_logger("AntoniobotInterface"),"Something went wrong while interacting with port " << port_);
            return CallbackReturn::FAILURE;
        }
        RCLCPP_INFO(rclcpp::get_logger("AntoniobotInterface"),"Hardware started, ready to take commands!");
        return CallbackReturn::SUCCESS;   
    }

    CallbackReturn AntoniobotInterface::on_deactivate(const rclcpp_lifecycle::State & previous_state)
    {
        RCLCPP_INFO(rclcpp::get_logger("AntoniobotInterface"),"Stopping the robot hardware...");
        if(arduino_socket.IsOpen())
        {
            try
            {
                arduino_socket.Close();
            }
            catch(...)
            {
                RCLCPP_FATAL_STREAM(rclcpp::get_logger("AntoniobotInterface"),"Something went wrong while closing the connection with port " << port_);
            }
            
        }
        RCLCPP_INFO(rclcpp::get_logger("AntoniobotInterface"),"Hardware stopped!");
        return CallbackReturn::SUCCESS;   
    }

    hardware_interface::return_type AntoniobotInterface::read(const rclcpp::Time & time, const rclcpp::Duration & period)
    {
        position_states_ = position_commands_; //In this case we have not a feedback, so we set the position equal to the command!
        return hardware_interface::return_type::OK;
    }

    void AntoniobotInterface::append_command(std::string &message,double angle,bool reverse)
    {
        int ang {0};
        if(reverse){
            ang = 180 - static_cast<int>(((angle + (M_PI/2))*180)/ M_PI);
        }
        else{
            ang = static_cast<int>(((angle + (M_PI/2))*180)/ M_PI);
        }
        message.append(std::to_string(ang));
        message.append(",");
    }

    bool AntoniobotInterface::write_to_arduino(std::string &message){
         try
        {
            RCLCPP_INFO_STREAM(rclcpp::get_logger("AntoniobotInterface"),"Message sent: "<< message);
            arduino_socket.Write(message);
            return true;
        }
        catch(...)
        {
            RCLCPP_ERROR_STREAM(rclcpp::get_logger("AntoniobotInterface"),"Something went wrong while sending the message "<< message);
            return false;  
        }
    }
    hardware_interface::return_type AntoniobotInterface::write(const rclcpp::Time & time, const rclcpp::Duration & period)
    {
        if(position_commands_ == previous_position_commands_)
        {   
            if (send_to_arduino){
                std::string start {"17"};
                if (!write_to_arduino(start)){ return hardware_interface::return_type::ERROR; }
                std::this_thread::sleep_for(std::chrono::milliseconds(400));
                std::string msg;
                for(size_t i = 0; i < info_.joints.size(); i++ ){
                    append_command(msg,position_commands_.at(i),false); //base
                }

                if (!write_to_arduino(msg)){ return hardware_interface::return_type::ERROR; }
                send_to_arduino = false;

            }
            
            return hardware_interface::return_type::OK;
        }
        
        // Sleep for 2 seconds
        // std::this_thread::sleep_for(std::chrono::milliseconds(400));
        // std::this_thread::sleep_for(std::chrono::milliseconds(400));
        send_to_arduino = true; 

        previous_position_commands_ = position_commands_;
        return hardware_interface::return_type::OK;
    }

}

PLUGINLIB_EXPORT_CLASS(antoniobot_controller::AntoniobotInterface, hardware_interface::SystemInterface);