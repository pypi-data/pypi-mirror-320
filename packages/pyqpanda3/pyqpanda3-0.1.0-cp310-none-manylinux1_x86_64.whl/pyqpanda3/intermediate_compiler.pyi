def convert_originir_file_to_qprog(*args, **kwargs):
    """convert_originir_file_to_qprog(ir_filepath: str) -> QPanda::QProg


    @brief This interface converts a file containing instruction set string in OriginIR format into the quantum program QProg.

    @param[in] ir_filepath File path to be converted containing OriginIR instruction set string.
    @return The Converted quantum program QProg.
          
    """
def convert_originir_string_to_qprog(*args, **kwargs):
    """convert_originir_string_to_qprog(string: str) -> QPanda::QProg


    @brief This interface converts instruction set string in OriginIR format into the quantum program QProg.

    @param[in] ir_str OriginIR instruction set string to be converted.
    @return The Converted quantum program QProg.
      
    """
def convert_qasm_file_to_qprog(*args, **kwargs):
    """convert_qasm_file_to_qprog(qasm_filepath: str) -> QPanda::QProg


    @brief This interface converts a file containing instruction set string in QASM format into the quantum program QProg.

    @param[in] qasm_filepath File path to be converted containing QASM instruction set string.
    @return The Converted quantum program QProg.
          
    """
def convert_qasm_string_to_qprog(*args, **kwargs):
    """convert_qasm_string_to_qprog(qasm_str: str) -> QPanda::QProg


    @brief This interface converts instruction set string in QASM format into the quantum program QProg.

    @param[in] qasm_str QASM instruction set string to be converted.
    @return The Converted quantum program QProg.
          
    """
def convert_qprog_to_originir(prog) -> str:
    """convert_qprog_to_originir(prog: QPanda::QProg) -> str


    @brief This interface converts the quantum program QProg to an instruction set string in OriginIR format.

    @param[in] prog The quantum program to be converted.
    @return The Converted OriginIR instruction set string.
          
    """
