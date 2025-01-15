#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <iostream>
#include <fstream>
#include <iomanip>
#include <string>
#include <ctime>
#include <vector>

using namespace std;

// Structure to hold hydrodynamic data and component efficiencies
struct HydroData {
    double area, velocity, density, gravity, head;
    double efficiencyTurbine, efficiencyGenerator, efficiencyOther;
    int operatingDays;
};

// Function to calculate the power output using the combined efficiencies of multiple components
double calculatePowerOutput(const HydroData& data) {
    double discharge = data.area * data.velocity;  // Calculate flow discharge
    double massFlowRate = discharge * data.density;  // Calculate mass flow rate
    double totalEfficiency = data.efficiencyTurbine * data.efficiencyGenerator * data.efficiencyOther / 1000000;  // Total system efficiency
    return massFlowRate * data.gravity * data.head * totalEfficiency;  // Calculate total power output
}

// Function to log messages
void logMessage(const string &message) {
    ofstream logFile("hydro_calculator.log", ios_base::app);
    if (logFile.is_open()) {
        time_t now = time(0);
        char* dt = ctime(&now);
        logFile << dt << ": " << message << endl;
        logFile.close();
    } else {
        cerr << "Unable to open log file." << endl;
    }
}

// Function to load hydrodynamic data from a file
bool loadHydroData(const string& filename, HydroData& data) {
    ifstream inFile(filename);
    if (!inFile) {
        cerr << "Error: Could not open the input file." << endl;
        logMessage("Error: Could not open the input file.");
        return false;
    }
    inFile >> data.area >> data.velocity >> data.density >> data.gravity >> data.head
           >> data.efficiencyTurbine >> data.efficiencyGenerator >> data.efficiencyOther >> data.operatingDays;
    inFile.close();
    return true;
}

// Function to save power output to a file
bool savePowerOutput(const string& filename, double powerOutput) {
    ofstream outFile(filename);
    if (!outFile) {
        cerr << "Error: Could not open the output file." << endl;
        logMessage("Error: Could not open the output file.");
        return false;
    }
    outFile << fixed << setprecision(2) << powerOutput;
    outFile.close();
    return true;
}

// Function to calculate average power output from multiple data sets
double calculateAveragePowerOutput(const vector<HydroData>& dataSets) {
    double totalPower = 0.0;
    for (const auto& data : dataSets) {
        totalPower += calculatePowerOutput(data);
    }
    return totalPower / dataSets.size();
}

// Function to load multiple hydrodynamic data sets from a file
bool loadMultipleHydroData(const string& filename, vector<HydroData>& dataSets) {
    ifstream inFile(filename);
    if (!inFile) {
        cerr << "Error: Could not open the input file." << endl;
        logMessage("Error: Could not open the input file.");
        return false;
    }
    HydroData data;
    while (inFile >> data.area >> data.velocity >> data.density >> data.gravity >> data.head
                  >> data.efficiencyTurbine >> data.efficiencyGenerator >> data.efficiencyOther >> data.operatingDays) {
        dataSets.push_back(data);
    }
    inFile.close();
    return true;
}

// Main function that orchestrates the reading, calculating, and output writing
int main_func() {
    vector<HydroData> dataSets;
    if (!loadMultipleHydroData("hydro_input.txt", dataSets)) return 1;  // Check if data loading is successful

    double averagePowerOutput = calculateAveragePowerOutput(dataSets);  // Compute the average power output
    logMessage("Calculated average power output: " + to_string(averagePowerOutput) + " watts.");

    if (!savePowerOutput("hydro_output.txt", averagePowerOutput)) return 1;  // Save the power output

    return 0;
}

PYBIND11_MODULE(Tan_Soon_Seng, m) {
    m.doc() = R"pbdoc(
        A demonstration of using C++ code
        in Python by packaging the former
        in a Python package using pybind11.

        ----------------------------------

        For use of:
        KIG2013 Programming Assignment
    )pbdoc";

    m.def("calculatePowerOutput", &calculatePowerOutput, "Function to calculate the power output using the combined efficiencies of multiple components.");
    m.def("logMessage", &logMessage, "Function to log messages.");
    m.def("loadHydroData", &loadHydroData, "Function to load hydrodynamic data from a file.");
    m.def("savePowerOutput", &savePowerOutput, "Function to save power output to a file.");
    m.def("calculateAveragePowerOutput", &calculateAveragePowerOutput, "Function to calculate average power output from multiple data sets.");
    m.def("loadMultipleHydroData", &loadMultipleHydroData, "Function to load multiple hydrodynamic data sets from a file.");
    m.def("main_func", &main_func, "Main function that orchestrates the reading, calculating, and output writing.");
}