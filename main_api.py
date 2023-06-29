import getopt
import sys
import json

from globalFunctions import localTimeConverter
from ApiGetter import get_project_creation_date,get_merge_requests

def printUsage():
    """Prints the usage syntax of the app."""
    print('usage : (default) ')
    print('main.py -f <config_file.json>')
    print('usage: (overwrites config file for all projects) ')
    print('main.py -p [<projectids>,] -c <start date for vizualize> -e <end date to vizualize>') ##correction this line by adding -p

class Main:
    start_Date_Vizu = ""
    end_Date_Vizu = ""
    gitlabAuth = ""
    gitlabBaseUrl = ""
    project_ids=""


    def read_config(self, arg):
        with open(arg) as json_config_file:
            config_data = json.load(json_config_file)
            
            self.project_ids = config_data['parameters']['project_ids']
            self.start_Date_Vizu = config_data['parameters']['start_Date_Vizu']
            self.end_Date_Vizu = config_data['parameters']['end_Date_Vizu']
            self.gitlabAuth = config_data['gitlab']['auth_token']
            self.gitlabBaseUrl = config_data['gitlab']['base_url']
            self.get_all_project = config_data['parameters']['get_all_project']

            self.project_creation_date = get_project_creation_date(self.project_ids[0],self.gitlabAuth)
        
        config_data["general_info"]={"creation_date":self.project_creation_date}
        with open(arg, 'w') as f:
            json.dump(config_data, f, indent=4)

        return True


    def start(self):
        print("Parsing launch options")

        try:
            [opts, args] = getopt.getopt(sys.argv[1:], "p:c:e:f:", ["projectid=", "start_date=", "end_date=", "file="])
        except getopt.GetoptError:
            printUsage()
            sys.exit(2)
        for opt, arg in opts:
            if opt == '-f':
                self.read_config(arg)
            elif opt == '-p':
                self.project_ids =arg.split(",")
            elif opt == '-c':
                self.start_Date_Vizu = arg
            elif opt == '-e':
                self.end_Date_Vizu = arg

        if not self.project_ids:
            print("No project IDs found.")
            printUsage()
            exit(2)
        if not self.gitlabAuth:
            print("No gitlab auth token provided in the config file")
            exit(2)

        print("Creating Merge Requests Json file")

        self.generateJsonMR()

    def generateJsonMR(self):
        for project_id in self.project_ids:
            print(self.get_all_project)
            if self.get_all_project:
                print("get the whole Project",project_id,": from",self.project_creation_date)
                get_merge_requests(project_id, self.gitlabAuth)
            else:
                print("Project",project_id,"from",self.start_Date_Vizu,"to",self.end_Date_Vizu)
                self.start_Date_Vizu = localTimeConverter(self.start_Date_Vizu)
                self.end_Date_Vizu= localTimeConverter(self.end_Date_Vizu)
                get_merge_requests(project_id, self.gitlabAuth, self.start_Date_Vizu,self.end_Date_Vizu)


if __name__ == '__main__':
    main = Main()
    main.start()


