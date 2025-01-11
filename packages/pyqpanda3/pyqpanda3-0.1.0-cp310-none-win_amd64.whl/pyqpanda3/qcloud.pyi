from typing import ClassVar, overload

Binary: DataBase
CLOUD_DEBUG: LogLevel
CLOUD_ERROR: LogLevel
CLOUD_INFO: LogLevel
CLOUD_WARNING: LogLevel
CONSOLE: LogOutput
FILE: LogOutput
Hex: DataBase

class DataBase:
    __members__: ClassVar[dict] = ...  # read-only
    Binary: ClassVar[DataBase] = ...
    Hex: ClassVar[DataBase] = ...
    __entries: ClassVar[dict] = ...
    def __init__(self, value: int) -> None:
        """__init__(self: qcloud.DataBase, value: int) -> None"""
    def __eq__(self, other: object) -> bool:
        """__eq__(self: object, other: object) -> bool"""
    def __hash__(self) -> int:
        """__hash__(self: object) -> int"""
    def __index__(self) -> int:
        """__index__(self: qcloud.DataBase) -> int"""
    def __int__(self) -> int:
        """__int__(self: qcloud.DataBase) -> int"""
    def __ne__(self, other: object) -> bool:
        """__ne__(self: object, other: object) -> bool"""
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

class JobStatus:
    __members__: ClassVar[dict] = ...  # read-only
    COMPUTING: ClassVar[JobStatus] = ...
    FAILED: ClassVar[JobStatus] = ...
    FINISHED: ClassVar[JobStatus] = ...
    QUEUING: ClassVar[JobStatus] = ...
    WAITING: ClassVar[JobStatus] = ...
    __entries: ClassVar[dict] = ...
    def __init__(self, value: int) -> None:
        """__init__(self: qcloud.JobStatus, value: int) -> None"""
    def __eq__(self, other: object) -> bool:
        """__eq__(self: object, other: object) -> bool"""
    def __hash__(self) -> int:
        """__hash__(self: object) -> int"""
    def __index__(self) -> int:
        """__index__(self: qcloud.JobStatus) -> int"""
    def __int__(self) -> int:
        """__int__(self: qcloud.JobStatus) -> int"""
    def __ne__(self, other: object) -> bool:
        """__ne__(self: object, other: object) -> bool"""
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

class LogLevel:
    __members__: ClassVar[dict] = ...  # read-only
    CLOUD_DEBUG: ClassVar[LogLevel] = ...
    CLOUD_ERROR: ClassVar[LogLevel] = ...
    CLOUD_INFO: ClassVar[LogLevel] = ...
    CLOUD_WARNING: ClassVar[LogLevel] = ...
    __entries: ClassVar[dict] = ...
    def __init__(self, value: int) -> None:
        """__init__(self: qcloud.LogLevel, value: int) -> None"""
    def __eq__(self, other: object) -> bool:
        """__eq__(self: object, other: object) -> bool"""
    def __hash__(self) -> int:
        """__hash__(self: object) -> int"""
    def __index__(self) -> int:
        """__index__(self: qcloud.LogLevel) -> int"""
    def __int__(self) -> int:
        """__int__(self: qcloud.LogLevel) -> int"""
    def __ne__(self, other: object) -> bool:
        """__ne__(self: object, other: object) -> bool"""
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

class LogOutput:
    __members__: ClassVar[dict] = ...  # read-only
    CONSOLE: ClassVar[LogOutput] = ...
    FILE: ClassVar[LogOutput] = ...
    __entries: ClassVar[dict] = ...
    def __init__(self, value: int) -> None:
        """__init__(self: qcloud.LogOutput, value: int) -> None"""
    def __eq__(self, other: object) -> bool:
        """__eq__(self: object, other: object) -> bool"""
    def __hash__(self) -> int:
        """__hash__(self: object) -> int"""
    def __index__(self) -> int:
        """__index__(self: qcloud.LogOutput) -> int"""
    def __int__(self) -> int:
        """__int__(self: qcloud.LogOutput) -> int"""
    def __ne__(self, other: object) -> bool:
        """__ne__(self: object, other: object) -> bool"""
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

class NOISE_MODEL:
    __members__: ClassVar[dict] = ...  # read-only
    BITFLIP_KRAUS_OPERATOR: ClassVar[NOISE_MODEL] = ...
    BIT_PHASE_FLIP_OPERATOR: ClassVar[NOISE_MODEL] = ...
    DAMPING_KRAUS_OPERATOR: ClassVar[NOISE_MODEL] = ...
    DECOHERENCE_KRAUS_OPERATOR: ClassVar[NOISE_MODEL] = ...
    DEPHASING_KRAUS_OPERATOR: ClassVar[NOISE_MODEL] = ...
    DEPOLARIZING_KRAUS_OPERATOR: ClassVar[NOISE_MODEL] = ...
    PHASE_DAMPING_OPERATOR: ClassVar[NOISE_MODEL] = ...
    __entries: ClassVar[dict] = ...
    def __init__(self, value: int) -> None:
        """__init__(self: qcloud.NOISE_MODEL, value: int) -> None"""
    def __eq__(self, other: object) -> bool:
        """__eq__(self: object, other: object) -> bool"""
    def __hash__(self) -> int:
        """__hash__(self: object) -> int"""
    def __index__(self) -> int:
        """__index__(self: qcloud.NOISE_MODEL) -> int"""
    def __int__(self) -> int:
        """__int__(self: qcloud.NOISE_MODEL) -> int"""
    def __ne__(self, other: object) -> bool:
        """__ne__(self: object, other: object) -> bool"""
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

class QCloudBackend:
    def __init__(self, arg0: str) -> None:
        """__init__(self: qcloud.QCloudBackend, arg0: str) -> None


                    @brief Initializes a QCloudBackend with a given backend name.
                    @param[in] backend_name The name of the quantum cloud backend.
        """
    @overload
    def expval_hamiltonian(self, prog, hamiltonian, qubits: list[int]) -> float:
        """expval_hamiltonian(*args, **kwargs)
        Overloaded function.

        1. expval_hamiltonian(self: qcloud.QCloudBackend, prog: QPanda::QProg, hamiltonian: QPanda::Hamiltonian, qubits: list[int]) -> float

        2. expval_hamiltonian(self: qcloud.QCloudBackend, prog: QPanda::QProg, hamiltonian: QPanda::Hamiltonian, options: qcloud.QCloudOptions) -> float
        """
    @overload
    def expval_hamiltonian(self, prog, hamiltonian, options: QCloudOptions) -> float:
        """expval_hamiltonian(*args, **kwargs)
        Overloaded function.

        1. expval_hamiltonian(self: qcloud.QCloudBackend, prog: QPanda::QProg, hamiltonian: QPanda::Hamiltonian, qubits: list[int]) -> float

        2. expval_hamiltonian(self: qcloud.QCloudBackend, prog: QPanda::QProg, hamiltonian: QPanda::Hamiltonian, options: qcloud.QCloudOptions) -> float
        """
    @overload
    def expval_pauli_operator(self, prog, pauli_operator, qubits: list[int]) -> float:
        """expval_pauli_operator(*args, **kwargs)
        Overloaded function.

        1. expval_pauli_operator(self: qcloud.QCloudBackend, prog: QPanda::QProg, pauli_operator: QPanda::PauliOperator, qubits: list[int]) -> float

        2. expval_pauli_operator(self: qcloud.QCloudBackend, prog: QPanda::QProg, pauli_operator: QPanda::PauliOperator, options: qcloud.QCloudOptions) -> float
        """
    @overload
    def expval_pauli_operator(self, prog, pauli_operator, options: QCloudOptions) -> float:
        """expval_pauli_operator(*args, **kwargs)
        Overloaded function.

        1. expval_pauli_operator(self: qcloud.QCloudBackend, prog: QPanda::QProg, pauli_operator: QPanda::PauliOperator, qubits: list[int]) -> float

        2. expval_pauli_operator(self: qcloud.QCloudBackend, prog: QPanda::QProg, pauli_operator: QPanda::PauliOperator, options: qcloud.QCloudOptions) -> float
        """
    def get_chip_topology(self) -> dict[int, list[QubitEdge]]:
        """get_chip_topology(self: qcloud.QCloudBackend) -> dict[int, list[qcloud.QubitEdge]]


                    @brief Retrieves the chip topology for a given chip name.
                    @param[in] chip_name The name of the chip.
                    @return The chip topology as a `ChipConfig` object.
        """
    def name(self) -> str:
        """name(self: qcloud.QCloudBackend) -> str


                    @brief Retrieves the name of the quantum cloud backend.
                    @return The name of the backend.
        """
    @overload
    def run(self, prog, shots: int, model: QCloudNoiseModel = ...) -> QCloudJob:
        """run(*args, **kwargs)
        Overloaded function.

        1. run(self: qcloud.QCloudBackend, prog: QPanda::QProg, shots: int, model: qcloud.QCloudNoiseModel = <qcloud.QCloudNoiseModel object at 0x000001CE07A437F0>) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified qubits and noise model (optional).
                    @param[in] prog The quantum program to run.
                    @param[in] shots The number of shots to run.
                    @param[in] model The noise model to apply during execution (optional).
                    @return A `QCloudJob` object representing the job.

        2. run(self: qcloud.QCloudBackend, prog: QPanda::QProg, qubits: list[int]) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified qubits.
                    @param[in] prog The quantum program to run.
                    @param[in] qubits The list of qubits to run the program on.
                    @return A `QCloudJob` object representing the job.

        3. run(self: qcloud.QCloudBackend, prog: QPanda::QProg, qubits: std::initializer_list<unsigned __int64>) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified qubits using an initializer list.
                    @param[in] prog The quantum program to run.
                    @param[in] qubits The list of qubits to run the program on.
                    @return A `QCloudJob` object representing the job.

        4. run(self: qcloud.QCloudBackend, prog: QPanda::QProg, shots: int, options: qcloud.QCloudOptions) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified options.
                    @param[in] prog The quantum program to run.
                    @param[in] shots The number of shots to run.
                    @param[in] options The options for running the program.
                    @return A `QCloudJob` object representing the job.

        5. run(self: qcloud.QCloudBackend, prog: list[QPanda::QProg], shots: int, options: qcloud.QCloudOptions) -> qcloud.QCloudJob


                    @brief Runs multiple quantum programs on the backend with specified options.
                    @param[in] prog The list of quantum programs to run.
                    @param[in] shots The number of shots to run.
                    @param[in] options The options for running the programs.
                    @return A `QCloudJob` object representing the job.

        6. run(self: qcloud.QCloudBackend, prog: QPanda::QProg, amplitudes: list[str]) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified amplitude list.
                    @param[in] prog The quantum program to run.
                    @param[in] amplitudes A list of amplitude names to run the program on.
                    @return A `QCloudJob` object representing the job.

        7. run(self: qcloud.QCloudBackend, prog: QPanda::QProg, amplitude: str) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with a single amplitude.
                    @param[in] prog The quantum program to run.
                    @param[in] amplitude The name of the amplitude to run the program on.
                    @return A `QCloudJob` object representing the job.
        """
    @overload
    def run(self, prog, qubits: list[int]) -> QCloudJob:
        """run(*args, **kwargs)
        Overloaded function.

        1. run(self: qcloud.QCloudBackend, prog: QPanda::QProg, shots: int, model: qcloud.QCloudNoiseModel = <qcloud.QCloudNoiseModel object at 0x000001CE07A437F0>) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified qubits and noise model (optional).
                    @param[in] prog The quantum program to run.
                    @param[in] shots The number of shots to run.
                    @param[in] model The noise model to apply during execution (optional).
                    @return A `QCloudJob` object representing the job.

        2. run(self: qcloud.QCloudBackend, prog: QPanda::QProg, qubits: list[int]) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified qubits.
                    @param[in] prog The quantum program to run.
                    @param[in] qubits The list of qubits to run the program on.
                    @return A `QCloudJob` object representing the job.

        3. run(self: qcloud.QCloudBackend, prog: QPanda::QProg, qubits: std::initializer_list<unsigned __int64>) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified qubits using an initializer list.
                    @param[in] prog The quantum program to run.
                    @param[in] qubits The list of qubits to run the program on.
                    @return A `QCloudJob` object representing the job.

        4. run(self: qcloud.QCloudBackend, prog: QPanda::QProg, shots: int, options: qcloud.QCloudOptions) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified options.
                    @param[in] prog The quantum program to run.
                    @param[in] shots The number of shots to run.
                    @param[in] options The options for running the program.
                    @return A `QCloudJob` object representing the job.

        5. run(self: qcloud.QCloudBackend, prog: list[QPanda::QProg], shots: int, options: qcloud.QCloudOptions) -> qcloud.QCloudJob


                    @brief Runs multiple quantum programs on the backend with specified options.
                    @param[in] prog The list of quantum programs to run.
                    @param[in] shots The number of shots to run.
                    @param[in] options The options for running the programs.
                    @return A `QCloudJob` object representing the job.

        6. run(self: qcloud.QCloudBackend, prog: QPanda::QProg, amplitudes: list[str]) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified amplitude list.
                    @param[in] prog The quantum program to run.
                    @param[in] amplitudes A list of amplitude names to run the program on.
                    @return A `QCloudJob` object representing the job.

        7. run(self: qcloud.QCloudBackend, prog: QPanda::QProg, amplitude: str) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with a single amplitude.
                    @param[in] prog The quantum program to run.
                    @param[in] amplitude The name of the amplitude to run the program on.
                    @return A `QCloudJob` object representing the job.
        """
    @overload
    def run(self, prog, qubits) -> QCloudJob:
        """run(*args, **kwargs)
        Overloaded function.

        1. run(self: qcloud.QCloudBackend, prog: QPanda::QProg, shots: int, model: qcloud.QCloudNoiseModel = <qcloud.QCloudNoiseModel object at 0x000001CE07A437F0>) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified qubits and noise model (optional).
                    @param[in] prog The quantum program to run.
                    @param[in] shots The number of shots to run.
                    @param[in] model The noise model to apply during execution (optional).
                    @return A `QCloudJob` object representing the job.

        2. run(self: qcloud.QCloudBackend, prog: QPanda::QProg, qubits: list[int]) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified qubits.
                    @param[in] prog The quantum program to run.
                    @param[in] qubits The list of qubits to run the program on.
                    @return A `QCloudJob` object representing the job.

        3. run(self: qcloud.QCloudBackend, prog: QPanda::QProg, qubits: std::initializer_list<unsigned __int64>) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified qubits using an initializer list.
                    @param[in] prog The quantum program to run.
                    @param[in] qubits The list of qubits to run the program on.
                    @return A `QCloudJob` object representing the job.

        4. run(self: qcloud.QCloudBackend, prog: QPanda::QProg, shots: int, options: qcloud.QCloudOptions) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified options.
                    @param[in] prog The quantum program to run.
                    @param[in] shots The number of shots to run.
                    @param[in] options The options for running the program.
                    @return A `QCloudJob` object representing the job.

        5. run(self: qcloud.QCloudBackend, prog: list[QPanda::QProg], shots: int, options: qcloud.QCloudOptions) -> qcloud.QCloudJob


                    @brief Runs multiple quantum programs on the backend with specified options.
                    @param[in] prog The list of quantum programs to run.
                    @param[in] shots The number of shots to run.
                    @param[in] options The options for running the programs.
                    @return A `QCloudJob` object representing the job.

        6. run(self: qcloud.QCloudBackend, prog: QPanda::QProg, amplitudes: list[str]) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified amplitude list.
                    @param[in] prog The quantum program to run.
                    @param[in] amplitudes A list of amplitude names to run the program on.
                    @return A `QCloudJob` object representing the job.

        7. run(self: qcloud.QCloudBackend, prog: QPanda::QProg, amplitude: str) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with a single amplitude.
                    @param[in] prog The quantum program to run.
                    @param[in] amplitude The name of the amplitude to run the program on.
                    @return A `QCloudJob` object representing the job.
        """
    @overload
    def run(self, prog, shots: int, options: QCloudOptions) -> QCloudJob:
        """run(*args, **kwargs)
        Overloaded function.

        1. run(self: qcloud.QCloudBackend, prog: QPanda::QProg, shots: int, model: qcloud.QCloudNoiseModel = <qcloud.QCloudNoiseModel object at 0x000001CE07A437F0>) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified qubits and noise model (optional).
                    @param[in] prog The quantum program to run.
                    @param[in] shots The number of shots to run.
                    @param[in] model The noise model to apply during execution (optional).
                    @return A `QCloudJob` object representing the job.

        2. run(self: qcloud.QCloudBackend, prog: QPanda::QProg, qubits: list[int]) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified qubits.
                    @param[in] prog The quantum program to run.
                    @param[in] qubits The list of qubits to run the program on.
                    @return A `QCloudJob` object representing the job.

        3. run(self: qcloud.QCloudBackend, prog: QPanda::QProg, qubits: std::initializer_list<unsigned __int64>) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified qubits using an initializer list.
                    @param[in] prog The quantum program to run.
                    @param[in] qubits The list of qubits to run the program on.
                    @return A `QCloudJob` object representing the job.

        4. run(self: qcloud.QCloudBackend, prog: QPanda::QProg, shots: int, options: qcloud.QCloudOptions) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified options.
                    @param[in] prog The quantum program to run.
                    @param[in] shots The number of shots to run.
                    @param[in] options The options for running the program.
                    @return A `QCloudJob` object representing the job.

        5. run(self: qcloud.QCloudBackend, prog: list[QPanda::QProg], shots: int, options: qcloud.QCloudOptions) -> qcloud.QCloudJob


                    @brief Runs multiple quantum programs on the backend with specified options.
                    @param[in] prog The list of quantum programs to run.
                    @param[in] shots The number of shots to run.
                    @param[in] options The options for running the programs.
                    @return A `QCloudJob` object representing the job.

        6. run(self: qcloud.QCloudBackend, prog: QPanda::QProg, amplitudes: list[str]) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified amplitude list.
                    @param[in] prog The quantum program to run.
                    @param[in] amplitudes A list of amplitude names to run the program on.
                    @return A `QCloudJob` object representing the job.

        7. run(self: qcloud.QCloudBackend, prog: QPanda::QProg, amplitude: str) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with a single amplitude.
                    @param[in] prog The quantum program to run.
                    @param[in] amplitude The name of the amplitude to run the program on.
                    @return A `QCloudJob` object representing the job.
        """
    @overload
    def run(self, prog, shots: int, options: QCloudOptions) -> QCloudJob:
        """run(*args, **kwargs)
        Overloaded function.

        1. run(self: qcloud.QCloudBackend, prog: QPanda::QProg, shots: int, model: qcloud.QCloudNoiseModel = <qcloud.QCloudNoiseModel object at 0x000001CE07A437F0>) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified qubits and noise model (optional).
                    @param[in] prog The quantum program to run.
                    @param[in] shots The number of shots to run.
                    @param[in] model The noise model to apply during execution (optional).
                    @return A `QCloudJob` object representing the job.

        2. run(self: qcloud.QCloudBackend, prog: QPanda::QProg, qubits: list[int]) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified qubits.
                    @param[in] prog The quantum program to run.
                    @param[in] qubits The list of qubits to run the program on.
                    @return A `QCloudJob` object representing the job.

        3. run(self: qcloud.QCloudBackend, prog: QPanda::QProg, qubits: std::initializer_list<unsigned __int64>) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified qubits using an initializer list.
                    @param[in] prog The quantum program to run.
                    @param[in] qubits The list of qubits to run the program on.
                    @return A `QCloudJob` object representing the job.

        4. run(self: qcloud.QCloudBackend, prog: QPanda::QProg, shots: int, options: qcloud.QCloudOptions) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified options.
                    @param[in] prog The quantum program to run.
                    @param[in] shots The number of shots to run.
                    @param[in] options The options for running the program.
                    @return A `QCloudJob` object representing the job.

        5. run(self: qcloud.QCloudBackend, prog: list[QPanda::QProg], shots: int, options: qcloud.QCloudOptions) -> qcloud.QCloudJob


                    @brief Runs multiple quantum programs on the backend with specified options.
                    @param[in] prog The list of quantum programs to run.
                    @param[in] shots The number of shots to run.
                    @param[in] options The options for running the programs.
                    @return A `QCloudJob` object representing the job.

        6. run(self: qcloud.QCloudBackend, prog: QPanda::QProg, amplitudes: list[str]) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified amplitude list.
                    @param[in] prog The quantum program to run.
                    @param[in] amplitudes A list of amplitude names to run the program on.
                    @return A `QCloudJob` object representing the job.

        7. run(self: qcloud.QCloudBackend, prog: QPanda::QProg, amplitude: str) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with a single amplitude.
                    @param[in] prog The quantum program to run.
                    @param[in] amplitude The name of the amplitude to run the program on.
                    @return A `QCloudJob` object representing the job.
        """
    @overload
    def run(self, prog, amplitudes: list[str]) -> QCloudJob:
        """run(*args, **kwargs)
        Overloaded function.

        1. run(self: qcloud.QCloudBackend, prog: QPanda::QProg, shots: int, model: qcloud.QCloudNoiseModel = <qcloud.QCloudNoiseModel object at 0x000001CE07A437F0>) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified qubits and noise model (optional).
                    @param[in] prog The quantum program to run.
                    @param[in] shots The number of shots to run.
                    @param[in] model The noise model to apply during execution (optional).
                    @return A `QCloudJob` object representing the job.

        2. run(self: qcloud.QCloudBackend, prog: QPanda::QProg, qubits: list[int]) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified qubits.
                    @param[in] prog The quantum program to run.
                    @param[in] qubits The list of qubits to run the program on.
                    @return A `QCloudJob` object representing the job.

        3. run(self: qcloud.QCloudBackend, prog: QPanda::QProg, qubits: std::initializer_list<unsigned __int64>) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified qubits using an initializer list.
                    @param[in] prog The quantum program to run.
                    @param[in] qubits The list of qubits to run the program on.
                    @return A `QCloudJob` object representing the job.

        4. run(self: qcloud.QCloudBackend, prog: QPanda::QProg, shots: int, options: qcloud.QCloudOptions) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified options.
                    @param[in] prog The quantum program to run.
                    @param[in] shots The number of shots to run.
                    @param[in] options The options for running the program.
                    @return A `QCloudJob` object representing the job.

        5. run(self: qcloud.QCloudBackend, prog: list[QPanda::QProg], shots: int, options: qcloud.QCloudOptions) -> qcloud.QCloudJob


                    @brief Runs multiple quantum programs on the backend with specified options.
                    @param[in] prog The list of quantum programs to run.
                    @param[in] shots The number of shots to run.
                    @param[in] options The options for running the programs.
                    @return A `QCloudJob` object representing the job.

        6. run(self: qcloud.QCloudBackend, prog: QPanda::QProg, amplitudes: list[str]) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified amplitude list.
                    @param[in] prog The quantum program to run.
                    @param[in] amplitudes A list of amplitude names to run the program on.
                    @return A `QCloudJob` object representing the job.

        7. run(self: qcloud.QCloudBackend, prog: QPanda::QProg, amplitude: str) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with a single amplitude.
                    @param[in] prog The quantum program to run.
                    @param[in] amplitude The name of the amplitude to run the program on.
                    @return A `QCloudJob` object representing the job.
        """
    @overload
    def run(self, prog, amplitude: str) -> QCloudJob:
        """run(*args, **kwargs)
        Overloaded function.

        1. run(self: qcloud.QCloudBackend, prog: QPanda::QProg, shots: int, model: qcloud.QCloudNoiseModel = <qcloud.QCloudNoiseModel object at 0x000001CE07A437F0>) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified qubits and noise model (optional).
                    @param[in] prog The quantum program to run.
                    @param[in] shots The number of shots to run.
                    @param[in] model The noise model to apply during execution (optional).
                    @return A `QCloudJob` object representing the job.

        2. run(self: qcloud.QCloudBackend, prog: QPanda::QProg, qubits: list[int]) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified qubits.
                    @param[in] prog The quantum program to run.
                    @param[in] qubits The list of qubits to run the program on.
                    @return A `QCloudJob` object representing the job.

        3. run(self: qcloud.QCloudBackend, prog: QPanda::QProg, qubits: std::initializer_list<unsigned __int64>) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified qubits using an initializer list.
                    @param[in] prog The quantum program to run.
                    @param[in] qubits The list of qubits to run the program on.
                    @return A `QCloudJob` object representing the job.

        4. run(self: qcloud.QCloudBackend, prog: QPanda::QProg, shots: int, options: qcloud.QCloudOptions) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified options.
                    @param[in] prog The quantum program to run.
                    @param[in] shots The number of shots to run.
                    @param[in] options The options for running the program.
                    @return A `QCloudJob` object representing the job.

        5. run(self: qcloud.QCloudBackend, prog: list[QPanda::QProg], shots: int, options: qcloud.QCloudOptions) -> qcloud.QCloudJob


                    @brief Runs multiple quantum programs on the backend with specified options.
                    @param[in] prog The list of quantum programs to run.
                    @param[in] shots The number of shots to run.
                    @param[in] options The options for running the programs.
                    @return A `QCloudJob` object representing the job.

        6. run(self: qcloud.QCloudBackend, prog: QPanda::QProg, amplitudes: list[str]) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with specified amplitude list.
                    @param[in] prog The quantum program to run.
                    @param[in] amplitudes A list of amplitude names to run the program on.
                    @return A `QCloudJob` object representing the job.

        7. run(self: qcloud.QCloudBackend, prog: QPanda::QProg, amplitude: str) -> qcloud.QCloudJob


                    @brief Runs a quantum program on the backend with a single amplitude.
                    @param[in] prog The quantum program to run.
                    @param[in] amplitude The name of the amplitude to run the program on.
                    @return A `QCloudJob` object representing the job.
        """

class QCloudJob:
    def __init__(self, arg0: str) -> None:
        """__init__(self: qcloud.QCloudJob, arg0: str) -> None


                    @brief Initializes a QCloudJob with a job ID.
                    @param[in] job_id The ID of the quantum job.
        """
    def job_id(self) -> str:
        """job_id(self: qcloud.QCloudJob) -> str


                    @brief Retrieves the job ID.
                    @details If the job ID is empty, throws a runtime error.
                    @return The job ID.
        """
    def query(self, *args, **kwargs):
        """query(self: qcloud.QCloudJob) -> QPanda::QCloudResult


                    @brief Queries the quantum job for information.
                    @return A `QCloudResult` object containing the job query result.
        """
    def result(self, *args, **kwargs):
        """result(self: qcloud.QCloudJob) -> QPanda::QCloudResult


                    @brief Retrieves the result of the quantum job.
                    @return A `QCloudResult` object containing the job result.
        """
    def status(self) -> JobStatus:
        """status(self: qcloud.QCloudJob) -> qcloud.JobStatus


                    @brief Retrieves the current status of the quantum job.
                    @return The status of the job as a `JobStatus` enumeration value.
        """

class QCloudNoiseModel:
    @overload
    def __init__(self) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: qcloud.QCloudNoiseModel) -> None

        @brief Default constructor for QCloudNoiseModel.

        2. __init__(self: qcloud.QCloudNoiseModel, arg0: qcloud.NOISE_MODEL, arg1: list[float], arg2: list[float]) -> None


                    @brief Initializes a QCloudNoiseModel with a noise model and its parameters. 
                    @param[in] model The noise model. 
                    @param[in] single_p The single qubit noise parameters.
                    @param[in] double_p The double qubit noise parameters.
        """
    @overload
    def __init__(self, arg0: NOISE_MODEL, arg1: list[float], arg2: list[float]) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: qcloud.QCloudNoiseModel) -> None

        @brief Default constructor for QCloudNoiseModel.

        2. __init__(self: qcloud.QCloudNoiseModel, arg0: qcloud.NOISE_MODEL, arg1: list[float], arg2: list[float]) -> None


                    @brief Initializes a QCloudNoiseModel with a noise model and its parameters. 
                    @param[in] model The noise model. 
                    @param[in] single_p The single qubit noise parameters.
                    @param[in] double_p The double qubit noise parameters.
        """
    def get_double_params(self) -> list[float]:
        """get_double_params(self: qcloud.QCloudNoiseModel) -> list[float]


                    @brief Returns the double qubit noise parameters.
        """
    def get_noise_model(self) -> str:
        """get_noise_model(self: qcloud.QCloudNoiseModel) -> str


                    @brief Returns the current noise model as a string.
        """
    def get_single_params(self) -> list[float]:
        """get_single_params(self: qcloud.QCloudNoiseModel) -> list[float]


                    @brief Returns the single qubit noise parameters.
        """
    def is_enabled(self) -> bool:
        """is_enabled(self: qcloud.QCloudNoiseModel) -> bool


                    @brief Checks if the noise model is enabled.
        """
    def print(self) -> None:
        """print(self: qcloud.QCloudNoiseModel) -> None


                    @brief Prints the noise model and its parameters to the standard output.
        """
    def set_double_params(self, arg0: list[float]) -> None:
        """set_double_params(self: qcloud.QCloudNoiseModel, arg0: list[float]) -> None


                    @brief Sets the double qubit noise parameters. 
                    @param[in] double_p The double qubit noise parameters.
        """
    def set_single_params(self, arg0: list[float]) -> None:
        """set_single_params(self: qcloud.QCloudNoiseModel, arg0: list[float]) -> None


                    @brief Sets the single qubit noise parameters. 
                    @param[in] single The single qubit noise parameters.
        """
    def __eq__(self, arg0: QCloudNoiseModel) -> bool:
        """__eq__(self: qcloud.QCloudNoiseModel, arg0: qcloud.QCloudNoiseModel) -> bool


                    @brief Compares two QCloudNoiseModel objects for equality.
        """
    def __ne__(self, arg0: QCloudNoiseModel) -> bool:
        """__ne__(self: qcloud.QCloudNoiseModel, arg0: qcloud.QCloudNoiseModel) -> bool


                    @brief Compares two QCloudNoiseModel objects for inequality.
        """

class QCloudOptions:
    def __init__(self) -> None:
        """__init__(self: qcloud.QCloudOptions) -> None


                    @brief Default constructor for QCloudOptions.
                    @details Initializes all options to their default values.
        """
    @overload
    def get_custom_option(self, arg0: str) -> int:
        """get_custom_option(*args, **kwargs)
        Overloaded function.

        1. get_custom_option(self: qcloud.QCloudOptions, arg0: str) -> int


                    @brief Retrieves a custom option by key as an integer value.
                    @param[in] key The key of the custom option.
                    @return The value of the custom option as an integer.

        2. get_custom_option(self: qcloud.QCloudOptions, arg0: str) -> float


                    @brief Retrieves a custom option by key as a double value.
                    @param[in] key The key of the custom option.
                    @return The value of the custom option as a double.

        3. get_custom_option(self: qcloud.QCloudOptions, arg0: str) -> str


                    @brief Retrieves a custom option by key as a string value.
                    @param[in] key The key of the custom option.
                    @return The value of the custom option as a string.

        4. get_custom_option(self: qcloud.QCloudOptions, arg0: str) -> bool


                    @brief Retrieves a custom option by key as a boolean value.
                    @param[in] key The key of the custom option.
                    @return The value of the custom option as a boolean.
        """
    @overload
    def get_custom_option(self, arg0: str) -> float:
        """get_custom_option(*args, **kwargs)
        Overloaded function.

        1. get_custom_option(self: qcloud.QCloudOptions, arg0: str) -> int


                    @brief Retrieves a custom option by key as an integer value.
                    @param[in] key The key of the custom option.
                    @return The value of the custom option as an integer.

        2. get_custom_option(self: qcloud.QCloudOptions, arg0: str) -> float


                    @brief Retrieves a custom option by key as a double value.
                    @param[in] key The key of the custom option.
                    @return The value of the custom option as a double.

        3. get_custom_option(self: qcloud.QCloudOptions, arg0: str) -> str


                    @brief Retrieves a custom option by key as a string value.
                    @param[in] key The key of the custom option.
                    @return The value of the custom option as a string.

        4. get_custom_option(self: qcloud.QCloudOptions, arg0: str) -> bool


                    @brief Retrieves a custom option by key as a boolean value.
                    @param[in] key The key of the custom option.
                    @return The value of the custom option as a boolean.
        """
    @overload
    def get_custom_option(self, arg0: str) -> str:
        """get_custom_option(*args, **kwargs)
        Overloaded function.

        1. get_custom_option(self: qcloud.QCloudOptions, arg0: str) -> int


                    @brief Retrieves a custom option by key as an integer value.
                    @param[in] key The key of the custom option.
                    @return The value of the custom option as an integer.

        2. get_custom_option(self: qcloud.QCloudOptions, arg0: str) -> float


                    @brief Retrieves a custom option by key as a double value.
                    @param[in] key The key of the custom option.
                    @return The value of the custom option as a double.

        3. get_custom_option(self: qcloud.QCloudOptions, arg0: str) -> str


                    @brief Retrieves a custom option by key as a string value.
                    @param[in] key The key of the custom option.
                    @return The value of the custom option as a string.

        4. get_custom_option(self: qcloud.QCloudOptions, arg0: str) -> bool


                    @brief Retrieves a custom option by key as a boolean value.
                    @param[in] key The key of the custom option.
                    @return The value of the custom option as a boolean.
        """
    @overload
    def get_custom_option(self, arg0: str) -> bool:
        """get_custom_option(*args, **kwargs)
        Overloaded function.

        1. get_custom_option(self: qcloud.QCloudOptions, arg0: str) -> int


                    @brief Retrieves a custom option by key as an integer value.
                    @param[in] key The key of the custom option.
                    @return The value of the custom option as an integer.

        2. get_custom_option(self: qcloud.QCloudOptions, arg0: str) -> float


                    @brief Retrieves a custom option by key as a double value.
                    @param[in] key The key of the custom option.
                    @return The value of the custom option as a double.

        3. get_custom_option(self: qcloud.QCloudOptions, arg0: str) -> str


                    @brief Retrieves a custom option by key as a string value.
                    @param[in] key The key of the custom option.
                    @return The value of the custom option as a string.

        4. get_custom_option(self: qcloud.QCloudOptions, arg0: str) -> bool


                    @brief Retrieves a custom option by key as a boolean value.
                    @param[in] key The key of the custom option.
                    @return The value of the custom option as a boolean.
        """
    def get_custom_options(self) -> dict[str, int | float | str | bool]:
        """get_custom_options(self: qcloud.QCloudOptions) -> dict[str, Union[int, float, str, bool]]


                    @brief Retrieves all custom options.
                    @return A dictionary of all custom options, where keys are option names and values are the option values.
        """
    def has_custom_option(self, arg0: str) -> bool:
        """has_custom_option(self: qcloud.QCloudOptions, arg0: str) -> bool


                    @brief Checks if a custom option with the given key exists.
                    @param[in] key The key of the custom option.
                    @return True if the custom option exists, false otherwise.
        """
    def is_amend(self) -> bool:
        """is_amend(self: qcloud.QCloudOptions) -> bool


                    @brief Checks whether amendment is enabled.
                    @return A boolean indicating whether amendment is enabled.
        """
    def is_mapping(self) -> bool:
        """is_mapping(self: qcloud.QCloudOptions) -> bool


                    @brief Checks whether mapping is enabled.
                    @return A boolean indicating whether mapping is enabled.
        """
    def is_optimization(self) -> bool:
        """is_optimization(self: qcloud.QCloudOptions) -> bool


                    @brief Checks whether optimization is enabled.
                    @return A boolean indicating whether optimization is enabled.
        """
    def print(self) -> None:
        """print(self: qcloud.QCloudOptions) -> None


                    @brief Prints the current settings of the options.
        """
    def set_amend(self, arg0: bool) -> None:
        """set_amend(self: qcloud.QCloudOptions, arg0: bool) -> None


                    @brief Sets whether amendment is enabled.
                    @param[in] is_amend A boolean indicating whether amendment is enabled.
        """
    def set_custom_option(self, arg0: str, arg1: int | float | str | bool) -> None:
        """set_custom_option(self: qcloud.QCloudOptions, arg0: str, arg1: Union[int, float, str, bool]) -> None


                    @brief Sets a custom option with a given key and value.
                    @param[in] key The key for the custom option.
                    @param[in] value The value for the custom option, which can be int, double, string, or bool.
        """
    def set_mapping(self, arg0: bool) -> None:
        """set_mapping(self: qcloud.QCloudOptions, arg0: bool) -> None


                    @brief Sets whether mapping is enabled.
                    @param[in] is_mapping A boolean indicating whether mapping is enabled.
        """
    def set_optimization(self, arg0: bool) -> None:
        """set_optimization(self: qcloud.QCloudOptions, arg0: bool) -> None


                    @brief Sets whether optimization is enabled.
                    @param[in] is_optimization A boolean indicating whether optimization is enabled.
        """

class QCloudResult:
    def __init__(self, arg0: str) -> None:
        """__init__(self: qcloud.QCloudResult, arg0: str) -> None


                    @brief Initializes a QCloudResult from a result string.
                    @param[in] result_string A string containing the job result data.
        """
    def get_amplitude(self) -> complex:
        """get_amplitude(self: qcloud.QCloudResult) -> complex


                    @brief Retrieves the amplitude for a particular quantum state.
                    @return A complex number representing the amplitude.
        """
    def get_amplitude_list(self) -> list[complex]:
        """get_amplitude_list(self: qcloud.QCloudResult) -> list[complex]


                    @brief Retrieves the list of amplitudes for different quantum states.
                    @return A list of complex numbers representing the amplitudes for each state.
        """
    def get_counts(self, base: DataBase = ...) -> dict[str, int]:
        """get_counts(self: qcloud.QCloudResult, base: qcloud.DataBase = <DataBase.Binary: 0>) -> dict[str, int]


                    @brief Retrieves the counts for each state.
                    @return A map where the keys are the state strings and the values are the corresponding counts.
        """
    def get_counts_list(self, base: DataBase = ...) -> list[dict[str, int]]:
        """get_counts_list(self: qcloud.QCloudResult, base: qcloud.DataBase = <DataBase.Binary: 0>) -> list[dict[str, int]]


                    @brief Retrieves the list of counts for each state across different measurements.
                    @return A list of maps, each containing state strings as keys and corresponding counts as values.
        """
    def get_probs(self, base: DataBase = ...) -> dict[str, float]:
        """get_probs(self: qcloud.QCloudResult, base: qcloud.DataBase = <DataBase.Binary: 0>) -> dict[str, float]


                    @brief Retrieves the probabilities for each state.
                    @return A map where the keys are the state strings and the values are the corresponding probabilities.
        """
    def get_probs_list(self, base: DataBase = ...) -> list[dict[str, float]]:
        """get_probs_list(self: qcloud.QCloudResult, base: qcloud.DataBase = <DataBase.Binary: 0>) -> list[dict[str, float]]


                    @brief Retrieves the list of probabilities for each state across different measurements.
                    @return A list of maps, each containing state strings as keys and corresponding probabilities as values.
        """
    def job_status(self) -> JobStatus:
        """job_status(self: qcloud.QCloudResult) -> qcloud.JobStatus


                    @brief Retrieves the status of the quantum job.
                    @return A `JobStatus` enum representing the job status.
        """

class QCloudService:
    def __init__(self, api_key: str, url: str = ...) -> None:
        """__init__(self: qcloud.QCloudService, api_key: str, url: str = 'http://pyqanda-admin.qpanda.cn') -> None


                    @brief Initializes a QCloudService.
                    @param[in] API key for accessing the cloud service.
                    @param[in] URL of the cloud service (defaults to DEFAULT_URL).
        """
    def backend(self, *args, **kwargs):
        """backend(self: qcloud.QCloudService, arg0: str) -> QPanda::QCloudBackend


                    @brief Retrieves a backend by its name.
                    @param[in] backend_name The name of the backend.
                    @return A QCloudBackend object corresponding to the specified backend name.
        """
    def backends(self) -> list[str]:
        """backends(self: qcloud.QCloudService) -> list[str]


                    @brief Returns a list of available backend names.
                    @return A list of backend names as strings.
        """
    def setup_logging(self, output: LogOutput = ..., file_path: str = ...) -> None:
        """setup_logging(self: qcloud.QCloudService, output: qcloud.LogOutput = <LogOutput.CONSOLE: 0>, file_path: str = '') -> None


                    @brief Sets up the logging configuration.
                    @param[in] output The log output type (default is LogOutput::CONSOLE).
                    @param[in] file_path The file path for saving logs, optional.
        """

class QubitEdge:
    qubit: int
    weight: float
    def __init__(self, arg0: int, arg1: float) -> None:
        """__init__(self: qcloud.QubitEdge, arg0: int, arg1: float) -> None


                    @brief Initializes a QubitEdge with a qubit index and a weight. 
                    @param[in] qubit The qubit index. 
                    @param[in] weight The weight of the edge.
        """
