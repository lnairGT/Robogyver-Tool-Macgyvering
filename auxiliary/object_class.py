# Define an object class that has different attributes - predicted pierceability, actual pierceability, material class, predicted grasp-ability, actual grasp-ability.
# Further specifies the object position and name

class MG_object:
    def __init__(self, obj_name, obj_position):
        # Initialize object with name and position
        self.obj_name = obj_name
        self.obj_position = obj_position

        # Object attributes
        self.pierce_predict = None
        self.pierce_actual = None
        self.material_class = None
        self.grasp_predict = None
        self.grasp_actual = None

        # Permissible values 
        self.pierce_values = [None, 1, 0]
        #self.material_values = ['plastic', 'fabric', 'paper', 'wood', 'metal', 'foam']
        self.material_values = ['plastic', 'wood', 'metal', 'foam', 'paper']

    def set_attribute(self, attribute, value):
        if attribute == 'pierce_predict':
            if value not in self.pierce_values:
                raise AttributeError('Incorrect value specified to pierce_predict attribute')
            else:
                self.pierce_predict = value 
        elif attribute == 'pierce_actual':
            if value not in self.pierce_values:
                raise AttributeError('Incorrect value specified to pierce_actual attribute')
            else:
                self.pierce_actual = value
        elif attribute == 'grasp_predict':
            if value not in self.pierce_values:
                raise AttributeError('Incorrect value specified to grasp_predict attribute')
            else:
                self.grasp_predict = value
        elif attribute == 'grasp_actual':
            if value not in self.pierce_values:
                raise AttributeError('Incorrect value specified to grasp_actual attribute')
            else:
                self.grasp_actual = value
        elif attribute == 'material_class':
            if value not in range(len(self.material_values)):
                raise AttributeError('Incorrect value specified to material_class attribute')
            else:
                self.material_class = self.material_values[value]
        else:
            raise AttributeError('Incorrect attribute specified for instance of class MG_object')

    def set_pose(self, position):
        self.obj_position = position

    class AttributeError(Exception):
        pass

