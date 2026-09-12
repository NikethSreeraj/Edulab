"""EduSim catalog: every entry is searchable, paginated, and launchable."""

SIMULATOR_CATALOG = {
    "Physics": {
        "Mechanics": ["1D Motion", "2D Motion", "Projectile Motion", "Free Fall", "Newton's Laws", "Friction", "Inclined Plane", "Tension", "Pulley Systems", "Connected Bodies", "Circular Motion", "Centripetal Force", "Relative Motion", "Momentum", "Collision Lab", "Impulse", "Work", "Energy", "Power", "Springs", "Simple Harmonic Motion", "Pendulum", "Gravitation", "Satellite Motion"],
        "Rotation": ["Torque", "Angular Momentum", "Moment of Inertia", "Rolling Motion", "Rotational Kinematics", "Rotational Dynamics"],
        "Waves": ["Wave Motion", "Superposition", "Standing Waves", "String Waves", "Sound Waves", "Doppler Effect", "Resonance"],
        "Optics": ["Ray Optics", "Plane Mirror", "Spherical Mirror", "Refraction", "Total Internal Reflection", "Lens", "Lens Combinations", "Prism", "Optical Instruments", "Wave Optics", "Interference", "Diffraction", "Polarization"],
        "Electricity": ["Electric Charge", "Electric Field", "Electric Potential", "Capacitors", "DC Circuits", "Ohm's Law", "Kirchhoff's Laws", "Series/Parallel Circuits", "Wheatstone Bridge", "Potentiometer"],
        "Magnetism": ["Magnetic Field", "Current-carrying Wire", "Solenoid", "Force on Charge", "Force on Current", "Electromagnetic Induction", "Faraday's Law", "Lenz's Law", "AC Circuits", "Transformers"],
        "Modern Physics": ["Photoelectric Effect", "Atomic Models", "Bohr Model", "Nuclear Physics", "Radioactive Decay", "Half-life", "Mass-Energy", "Semiconductor", "Diode", "Transistor", "Logic Gates"],
    },
    "Chemistry": {
        "Atomic": ["Atomic Structure", "Electron Configuration", "Orbitals", "Quantum Numbers", "Periodic Trends", "Ion Formation"],
        "Molecular": ["Lewis Structures", "VSEPR", "Molecular Geometry", "Hybridization", "Bond Visualization", "Polarity"],
        "Reactions": ["Chemical Equation Balancing", "Reaction Visualization", "Stoichiometry", "Limiting Reagent", "Reaction Rates", "Collision Theory", "Energy Diagrams"],
        "Solutions": ["Concentration", "Molarity", "Dilution", "Solubility", "pH Simulator", "Buffers"],
        "Equilibrium": ["Dynamic Equilibrium", "Le Chatelier's Principle", "Equilibrium Concentration", "Kc/Kp Visualization"],
        "Electrochemistry": ["Galvanic Cell", "Electrolytic Cell", "Redox", "Cell Potential", "Ion Movement"],
        "Thermochemistry": ["Heat Transfer", "Enthalpy", "Exothermic/Endothermic Reactions", "Energy Profiles", "Calorimeter"],
        "Organic Chemistry": ["Molecule Builder", "Functional Groups", "Isomer Visualization", "Reaction Concept Visualization"],
        "Acids and Bases": ["Titration Simulator", "Neutralization", "Buffer", "Henderson-Hasselbalch"],
    },
    "Mathematics": {
        "Algebra": ["Linear Equations", "Quadratic Equations", "Polynomial Graphs", "Inequalities", "Sequences", "Series", "Complex Numbers"],
        "Functions": ["Function Grapher", "Quadratic Function", "Exponential Function", "Logarithmic Function", "Transformations", "Roots and Intersections"],
        "Coordinate Geometry": ["Straight Lines", "Circles", "Parabolas", "Ellipses", "Hyperbolas", "Distance and Section Formula", "Conic Sections"],
        "3D Geometry": ["3D Geometry Lab", "3D Coordinate System", "Points, Lines and Planes", "Vectors", "Angles", "Distances", "Intersections", "Octants"],
        "Calculus": ["Limits", "Derivative Visualizer", "Tangent Visualization", "Rate of Change", "Integration", "Area Under Curve", "Riemann Sums", "Differential Equations"],
        "Probability": ["Coin Simulator", "Dice Simulator", "Cards Simulator", "Random Variables", "Distributions", "Monte Carlo Simulation"],
        "Vectors": ["Vector Visualizer", "2D Vectors", "3D Vectors", "Vector Addition", "Dot Product", "Cross Product"],
    },
    "Computer Science": {
        "Programming": ["Code Editor", "Code Execution", "Code Assistant", "Debugging Lab", "Library Explorer", "Data Structures"],
        "Algorithms": ["Algorithm Visualizer", "Sorting Visualizer", "Searching Visualizer", "Graph Traversal", "BFS/DFS", "Complexity Explorer"],
        "Computer Systems": ["Binary and Hexadecimal", "Logic Gates", "CPU Instruction Cycle", "Memory Visualizer", "Network Packet Flow"],
    },
}


def flatten_simulators():
    items = []
    for subject, groups in SIMULATOR_CATALOG.items():
        for group, simulators in groups.items():
            for name in simulators:
                items.append({
                    "subject": subject,
                    "group": group,
                    "name": name,
                    "id": name.lower().replace("/", "-").replace("&", "and").replace(" ", "-"),
                })
    return items
