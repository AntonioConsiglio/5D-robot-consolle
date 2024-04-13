#ifndef ANTONIOBOT_INTERFACE_HPP_
#define ANTONIOBOT_INTERFACE_HPP_

#include <rclcpp/rclcpp.hpp>
#include <hardware_interface/system_interface.hpp>
#include <rclcpp_lifecycle/node_interfaces/lifecycle_node_interface.hpp>
#include <rclcpp_lifecycle/state.hpp>
#include <vector>

#include <libserial/SerialPort.h>
#include <string>

namespace antoniobot_controller
{

using CallbackReturn = rclcpp_lifecycle::node_interfaces::LifecycleNodeInterface::CallbackReturn;

class AntoniobotInterface : public hardware_interface::SystemInterface
{
public:
    AntoniobotInterface();
    virtual ~AntoniobotInterface();
    virtual CallbackReturn on_activate(const rclcpp_lifecycle::State & previous_state) override;
    virtual CallbackReturn on_deactivate(const rclcpp_lifecycle::State & previous_state) override;

    virtual CallbackReturn on_init(const hardware_interface::HardwareInfo & hardware_info) override;
    virtual std::vector<hardware_interface::StateInterface> export_state_interfaces() override;
    virtual std::vector<hardware_interface::CommandInterface> export_command_interfaces() override;

    virtual hardware_interface::return_type read(const rclcpp::Time & time, const rclcpp::Duration & period) override;
    virtual hardware_interface::return_type write(const rclcpp::Time & time, const rclcpp::Duration & period) override;

    void append_command(std::string &message,double angle,bool reverse);
    bool write_to_arduino(std::string &message);
private:
    LibSerial::SerialPort arduino_socket;
    std::string port_;
    bool send_to_arduino;

    std::vector<double> position_commands_ ;
    std::vector<double> previous_position_commands_ ;
    std::vector<double> position_states_ ;
};
    
} // namespace antoniobot_arduino

#endif