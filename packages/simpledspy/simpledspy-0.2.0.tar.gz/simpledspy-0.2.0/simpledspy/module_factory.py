import dspy
from typing import List, Dict, Any

class ModuleFactory:
    def create_module(self, inputs: List[str], outputs: List[str], description: str = "") -> dspy.Module:
        """
        Creates a DSPy module with specified inputs and outputs.
        
        Args:
            inputs: List of input field names
            outputs: List of output field names
            description: Optional description of the module's purpose
            
        Returns:
            dspy.Module: Configured DSPy module
        """


        signature_fields = {}
        for inp in inputs:
            signature_fields[inp] = dspy.InputField(desc=f"Input field {inp}")
        for outp in outputs:
            signature_fields[outp] = dspy.OutputField(desc=f"Output field {outp}")




        # Create signature class with proper instructions
        instructions = description or f"Given the fields {', '.join(inputs)}, produce the fields {', '.join(outputs)}."
        Signature = type(
            'Signature',
            (dspy.Signature,),
            {
                '__doc__': instructions,
                **signature_fields
            }
        )

        # Create and return Predict module
        # print("Signature:", Signature)
        return dspy.Predict(Signature)
