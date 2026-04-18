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

class Technology_Diagram:
    node_list= {}
    edge_list = []
    dot_graph = pydot.Dot(graph_type='digraph')
        
    def node_creation(self, distinct_tools):
        for tool in distinct_tools:
            temp_tool = tool.lower()
            temp_tool = re.sub('\W+','', temp_tool )
            temp_node = pydot.Node(tool, fillcolor= "#ADD8E6", style="filled")
            self.node_list.__setitem__(
                    tool , {
                        "value": temp_node
                    }
            )
            self.dot_graph.add_node(temp_node)
            
    def check_edge_present(self, label, node_1, node_2):
        for edge in self.edge_list:
            if edge["head"] == node_1:
                if edge["tail"] == node_2:
                    temp_label = edge["label"] + f'  {label}'
                    edge["label"] = temp_label
                    return
            
        temp_dict = {
            "head": node_1,
            "tail": node_2,
            "label": label
        }
        self.edge_list.append(temp_dict)
        
    def edge_creation(self, label, node_1, node_2):
        temp_edge = pydot.Edge(node_1,node_2, arrowsize = 0.5, color = "#000000", penwidth = 0.7, fontsize = 8.0)
        temp_edge.set_label(label)
        self.dot_graph.add_edge(temp_edge)
        
    def isnan(self, value):
        try:
            import math
            return math.isnan(float(value))
        except:
            return False
        
    def create_edge(self, final_df):
        for i in range(0, final_df.shape[0]):
            current_tool = final_df.iat[i,6]
            pred_1 = final_df.iat[i,1]
            pred_2 = final_df.iat[i,2]
            pred_3 = final_df.iat[i,3]
            pred_4 = final_df.iat[i,4]
            pred_5 = final_df.iat[i,5]
            if self.isnan(pred_1) == False and pred_1 != "INIT":
                pred_tool = final_df.loc[final_df['S#'] == pred_1, 'Automation tool'].iloc[0]
                self.check_edge_present(f'A{pred_1}', self.node_list[pred_tool]["value"],self.node_list[current_tool]["value"])
            if self.isnan(pred_2) == False and pred_2 != "INIT":
                pred_tool = final_df.loc[final_df['S#'] == pred_2, 'Automation tool'].iloc[0]
                self.check_edge_present(f'A{pred_2}', self.node_list[pred_tool]["value"],self.node_list[current_tool]["value"])
            if self.isnan(pred_3) == False and pred_3 != "INIT":
                pred_tool = final_df.loc[final_df['S#'] == pred_3, 'Automation tool'].iloc[0]
                self.check_edge_present(f'A{pred_3}', self.node_list[pred_tool]["value"],self.node_list[current_tool]["value"])
            if self.isnan(pred_4) == False and pred_4 != "INIT":
                pred_tool = final_df.loc[final_df['S#'] == pred_4, 'Automation tool'].iloc[0]
                self.check_edge_present(f'A{pred_4}', self.node_list[pred_tool]["value"],self.node_list[current_tool]["value"])
            if self.isnan(pred_5) == False and pred_5 != "INIT":
                pred_tool = final_df.loc[final_df['S#'] == pred_5, 'Automation tool'].iloc[0]
                self.check_edge_present(f'A{pred_5}', self.node_list[pred_tool]["value"],self.node_list[current_tool]["value"])
                
        for edge in self.edge_list:
            self.edge_creation(edge["label"], edge["head"], edge["tail"])
                
    def output(self):
        output_file_png = "Technology_Diagram.png"
        output_file_svg = "Technology_Diagram.svg"
        self.dot_graph.write_raw("Diagram_Technology")
        #self.dot_graph.write_png(output_file_png)
        #self.dot_graph.write_svg(output_file_svg)
        
    def create_technology_diagram(self):
        #df = io.BytesIO(uploaded['Sample-QODE-Questionnaire.xlsm'])
        df = 'QODE-Questionnaire.xlsm'
        data_read = pd.read_excel(df, sheet_name="Q_Stories", header=3)[2:]
        #Let us Create an object 
        logger=logging.getLogger() 

        #Now we are going to Set the threshold of logger to DEBUG 
        logger.setLevel(logging.DEBUG) 
        logger.debug("creating_technology_diagram")
        logger.debug("data_read is done")
        logger.debug(data_read)
        Semi_Final_df = data_read[data_read['Yes / No'] == 'Yes']
        selected_columns = ["S#","Predecessor 1 (incl. INIT)","Predecessor 2 (optional)","Predecessor 3 (optional)","Predecessor 4 (optional)","Predecessor 5 (optional)","Automation tool"]
        final_columns = Semi_Final_df[selected_columns]
        final_df = final_columns.copy()
        distinct_tools = final_df["Automation tool"].unique()
        self.node_creation(distinct_tools)
        self.create_edge(final_df)
        self.output()     

if __name__ == "__main__":
  uac = Technology_Diagram()
  uaac = uac.create_technology_diagram() 