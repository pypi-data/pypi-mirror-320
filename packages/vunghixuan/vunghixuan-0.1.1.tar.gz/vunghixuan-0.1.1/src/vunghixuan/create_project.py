
# src/vunghixuan/create_project.py
import os 
from pathlib import Path

class Project:
    def __init__(self):       
        # self.root_path = Path(__file__).parent
        self.root_path = Path(os.getcwd())  # Lấy đường dẫn hiện tại
        # self.create_project()
    
    # def create_project(self):
    #     for folder, content in structure.items():
    #         if isinstance(content, dict):
    #             folder_path = os.path.join(self.root_path, folder)
    #             os.makedirs(folder_path) 
    #             self.create_project()
    #         else:
    #             with open(os.path.join(folder_path, 'models', '__init__.py'), 'w') as f:
    #                 f.write("# Init file for models\n")    

    # Tạo ra folder
    def create_folder(self, folder_path, name):
        folder_path = os.path.join(folder_path, name)
        os.makedirs(folder_path, exist_ok=True) 
    
    # Tạo ra folder apps
    def create_project(self):
        list_folder = ['apps', 'config', 'data_base']
        for folder in list_folder:
            self.create_folder(self.root_path, folder)

        

    def create_app(self, app_name):
        folder_path = os.path.join(self.root_path, 'apps')
        
        if not os.path.exists(folder_path):
            self.create_project()
            self.create_app(app_name)
        else:
            self.create_folder(folder_path, app_name)
            folder_path = os.path.join(self.root_path, 'apps', app_name)

            list_folder = ['models', 'views', 'controlers']
            for folder in list_folder:
                self.create_folder(folder_path, folder)



    
    
        
        


if __name__=="__main__":
    
    project = Project()

    # 1. Tạo ra project
    # project.create_project()

    # 2. Tạo app
    project.create_app('app1')
        