import io
import pandas as pd
#df = pd.read_excel(io.BytesIO(uploaded['Sample-QODE-Questionnaire.xlsm']))
df = pd.read_excel('QODE-Questionnaire.xlsm', sheet_name="Q_Stories")


from skimage import io
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from io import StringIO
import threading
import pydot
import asyncio
import time
import math
import sys
import webbrowser
import re
import os.path
import io
import os
import logging

class People_Diagram:
    node_list= {}
    dot_graph = pydot.Dot(graph_type='digraph')
        
    def node_creation(self, distinct_roles):
        for role in distinct_roles:
            temp_node = pydot.Node(role, fillcolor= "#ADD8E6", style="filled")
            temp_node.set_shape("box")
            self.node_list.__setitem__(
                    role , {
                        "value": temp_node
                    }
            )
            self.dot_graph.add_node(temp_node)
        
    def edge_creation(self, node_1, node_2, edge_color):
        temp_edge = pydot.Edge(node_1,node_2, arrowsize = 0.3, weight = 0.5 , color = edge_color, penwidth = 0.7, decorate = "true")
        self.dot_graph.add_edge(temp_edge)
        
    def isnan(self, value):
        try:
            import math
            return math.isnan(float(value))
        except:
            return False
        
    def create_edge(self, final_df):
        for i in range(0, final_df.shape[0]):
            current_role = final_df.iat[i,6]
            Total_time = final_df.iat[i,7]
            Manual_time = final_df.iat[i,8]
            pred_1 = final_df.iat[i,1]
            pred_2 = final_df.iat[i,2]
            pred_3 = final_df.iat[i,3]
            pred_4 = final_df.iat[i,4]
            pred_5 = final_df.iat[i,5]
            if (Total_time - Manual_time) != 0:
                color = "#000000"
            else:
                color = "#FFA500"
            if self.isnan(pred_1) == False and pred_1 != "INIT":
                pred_role = final_df.loc[final_df['S#'] == pred_1, 'Team / owner role'].iloc[0]
                self.edge_creation(self.node_list[pred_role]["value"],self.node_list[current_role]["value"], color)
            if self.isnan(pred_2) == False and pred_2 != "INIT":
                pred_role = final_df.loc[final_df['S#'] == pred_2, 'Team / owner role'].iloc[0]
                self.edge_creation(self.node_list[pred_role]["value"],self.node_list[current_role]["value"], color)
            if self.isnan(pred_3) == False and pred_3 != "INIT":
                pred_role = final_df.loc[final_df['S#'] == pred_3, 'Team / owner role'].iloc[0]
                self.edge_creation(self.node_list[pred_role]["value"],self.node_list[current_role]["value"], color)
            if self.isnan(pred_4) == False and pred_4 != "INIT":
                pred_role = final_df.loc[final_df['S#'] == pred_4, 'Team / owner role'].iloc[0]
                self.edge_creation(self.node_list[pred_role]["value"],self.node_list[current_role]["value"], color)
            if self.isnan(pred_5) == False and pred_5 != "INIT":
                pred_role = final_df.loc[final_df['S#'] == pred_5, 'Team / owner role'].iloc[0]
                self.edge_creation(self.node_list[pred_role]["value"],self.node_list[current_role]["value"], color)
                
    def output(self):
        output_file_png = "People_Diagram.png"
        output_file_svg = "People_Diagram.svg"
        self.dot_graph.write_raw("Diagram_People")
        #self.dot_graph.write_png(output_file_png)
        #self.dot_graph.write_svg(output_file_svg)
        
        
    def create_people_diagram(self):
        
        #df = io.BytesIO(uploaded['Sample-QODE-Questionnaire.xlsm'])
        df = 'QODE-Questionnaire.xlsm'
        data_read = pd.read_excel(df, sheet_name="Q_Stories", header=3)[2:]
        # Create an object 
        logger=logging.getLogger() 

        # Set the threshold of logger to DEBUG 
        logger.setLevel(logging.DEBUG) 
        logger.debug("creating_people_diagram")
        logger.debug("data_read is done")
        logger.debug(data_read)
        Semi_Final_df = data_read[data_read['Yes / No'] == 'Yes']
        selected_columns = ["S#","Predecessor 1 (incl. INIT)","Predecessor 2 (optional)","Predecessor 3 (optional)","Predecessor 4 (optional)","Predecessor 5 (optional)","Team / owner role","Total time taken","Manual time spent"]
        final_columns = Semi_Final_df[selected_columns]
        final_df = final_columns.copy()
        distinct_roles = final_df["Team / owner role"].unique()
        self.node_creation(distinct_roles)
        self.create_edge(final_df)
        self.output()

if __name__ == "__main__":
  uac = People_Diagram()
  uaac = uac.create_people_diagram()