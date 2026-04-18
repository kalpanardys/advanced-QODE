import io
import pandas as pd
#df = pd.read_excel(io.BytesIO('Sample-QODE-Questionnaire.xlsm'))
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

class Process_Diagram:

    node_list= {}
    timer_count = 0
    dot_graph = pydot.Dot(graph_type='digraph')
    Qode_graph = nx.DiGraph()
    
    
    def node_creation(self, lable, fillcolor, style, shape):
        qsd_node = pydot.Node(lable,fillcolor=fillcolor,style=style)
        qsd_node.set_shape(shape)
        self.dot_graph.add_node(qsd_node)
        return  qsd_node
    
    def edge_creation(self, lable, node_1,node_2):
        iedge = pydot.Edge(node_1,node_2)
        iedge.set_label(lable)
        self.dot_graph.add_edge(iedge)   
        
    def timer_delay(self):
        for i in range(1,99,2):
            time.sleep(1)
            self.timer_count += 1
        
    def isnan(self, value):
        try:
            import math
            return math.isnan(float(value))
        except:
            return False
        
    def criticality_mapping(self, value):
        if value.lower() == "hi":
            return 3
        if value.lower() == "med":
            return 2
        return 1
    
    def pydot_node_creation(self, final_df):
        self.node_list.__setitem__(
           0,{
                "value": self.node_creation('E0 \nRequirement \n (Jira)',"#ADD8E6","filled","box"),
                "time": 0,
                "node_no" : 'E0'
            }
        )
        
        for i in range(0, final_df.shape[0]):
            self.node_list.__setitem__(
                final_df.iat[i,0], {
                    "value":  self.node_creation(f'E{i+1} \n {final_df.iat[i,11]} to {final_df.iat[i,12]} \n ({final_df.iat[i,13]}) ',"#FFFFFF","filled","box"),
                    "time": 0,
                    "node_no": f'E{i+1}'
            })
    
    def calculate_lead_time(self, final_df, node_list):
        node_list[1]["time"] = final_df.iat[0,2]
        for i in range(0, final_df.shape[0]):
            current_node=final_df.iat[i,0]
            pred_1=final_df.iat[i,4]
            pred_2=final_df.iat[i,5]
            pred_3=final_df.iat[i,6]
            pred_4=final_df.iat[i,7]
            pred_5=final_df.iat[i,8]
            if self.isnan(pred_1)==False:
                if pred_1 == "INIT":
                    if( current_node != 1):
                        node_list[current_node]["time"] = round((final_df.iat[i,2] + node_list[1]["time"]),2)
                else:
                    if node_list[current_node]["time"] <= round((final_df.iat[i,2] + node_list[pred_1]["time"]),2):
                        node_list[current_node]["time"] = round((final_df.iat[i,2] + node_list[pred_1]["time"]),2)
            if self.isnan(pred_2)==False and pred_2 !="INIT":
                if node_list[current_node]["time"] <= round((final_df.iat[i,2] + node_list[pred_2]["time"]),2):
                    node_list[current_node]["time"] = round((final_df.iat[i,2] + node_list[pred_2]["time"]),2)
            if self.isnan(pred_3)== False and pred_3 !="INIT":
                if node_list[current_node]["time"] <= round((final_df.iat[i,2] + node_list[pred_3]["time"]),2):
                    node_list[current_node]["time"] = round((final_df.iat[i,2] + node_list[pred_3]["time"]),2)
            if self.isnan(pred_4) == False and pred_4 !="INIT":
                if node_list[current_node]["time"] <= round((final_df.iat[i,2] + node_list[pred_4]["time"]),2):
                    node_list[current_node]["time"] = round((final_df.iat[i,2] + node_list[pred_4]["time"]),2)
            if self.isnan(pred_5) == False and pred_5 !="INIT":
                if node_list[current_node]["time"] <= round((final_df.iat[i,2] + node_list[pred_5]["time"]),2):
                    node_list[current_node]["time"] = round((final_df.iat[i,2] + node_list[pred_5]["time"]),2) 
                    
        for i in range(0, final_df.shape[0]):
            current_node=final_df.iat[i,0]
            pred_1=final_df.iat[i,4]
            pred_2=final_df.iat[i,5]
            pred_3=final_df.iat[i,6]
            pred_4=final_df.iat[i,7]
            pred_5=final_df.iat[i,8]
            if self.isnan(pred_1)==False:
                if pred_1 == "INIT":
                    if( current_node != 1):
                        node_list[current_node]["time"] = round((final_df.iat[i,2] + node_list[1]["time"]),2)
                else:
                    if node_list[current_node]["time"] <= round((final_df.iat[i,2] + node_list[pred_1]["time"]),2):
                        node_list[current_node]["time"] = round((final_df.iat[i,2] + node_list[pred_1]["time"]),2)
            if self.isnan(pred_2)==False and pred_2 !="INIT":
                if node_list[current_node]["time"] <= round((final_df.iat[i,2] + node_list[pred_2]["time"]),2):
                    node_list[current_node]["time"] = round((final_df.iat[i,2] + node_list[pred_2]["time"]),2)
            if self.isnan(pred_3)== False and pred_3 !="INIT":
                if node_list[current_node]["time"] <= round((final_df.iat[i,2] + node_list[pred_3]["time"]),2):
                    node_list[current_node]["time"] = round((final_df.iat[i,2] + node_list[pred_3]["time"]),2)
            if self.isnan(pred_4) == False and pred_4 !="INIT":
                if node_list[current_node]["time"] <= round((final_df.iat[i,2] + node_list[pred_4]["time"]),2):
                    node_list[current_node]["time"] = round((final_df.iat[i,2] + node_list[pred_4]["time"]),2)
            if self.isnan(pred_5) == False and pred_5 !="INIT":
                if node_list[current_node]["time"] <= round((final_df.iat[i,2] + node_list[pred_5]["time"]),2):
                    node_list[current_node]["time"] = round((final_df.iat[i,2] + node_list[pred_5]["time"]),2) 
                    
    def pydot_edge_creation(self, final_df, node_list):
        self.edge_creation(f'A{1} \n {final_df.iat[0,2]},{final_df.iat[0,3]} (0) \n {final_df.iat[0,10]}',node_list[0]["value"],node_list[1]["value"])
        for i in range(0, final_df.shape[0]):
            current_node=final_df.iat[i,0]
            pred_1=final_df.iat[i,4]
            pred_2=final_df.iat[i,5]
            pred_3=final_df.iat[i,6]
            pred_4=final_df.iat[i,7]
            pred_5=final_df.iat[i,8]
            if self.isnan(pred_1)==False:
                if(pred_1 == "INIT"):
                    if( 1!=current_node):
                        self.edge_creation(f'A{current_node} \n {final_df.iat[i,2]},{final_df.iat[i,3]} ({node_list[1]["time"]}) \n {final_df.iat[i,10]}',node_list[1]["value"],node_list[current_node]["value"])
                else:
                    self.edge_creation(f'A{current_node} \n {final_df.iat[i,2]},{final_df.iat[i,3]} ({node_list[pred_1]["time"]}) \n {final_df.iat[i,10]}',node_list[pred_1]["value"],node_list[current_node]["value"])   
            if self.isnan(pred_2)==False and pred_2 !="INIT":
                self.edge_creation(f'A{current_node}(A) \n {final_df.iat[i,2]},{final_df.iat[i,3]} ({node_list[pred_2]["time"]}) \n {final_df.iat[i,10]}',node_list[pred_2]["value"],node_list[current_node]["value"])
            if self.isnan(pred_3)== False and pred_3 !="INIT":
                self.edge_creation(f'A{current_node}(B) \n {final_df.iat[i,2]},{final_df.iat[i,3]} ({node_list[pred_3]["time"]}) \n {final_df.iat[i,10]}',node_list[pred_3]["value"],node_list[current_node]["value"])
            if self.isnan(pred_4) == False and pred_4 !="INIT":
                self.edge_creation(f'A{current_node}(C) \n {final_df.iat[i,2]},{final_df.iat[i,3]} ({node_list[pred_4]["time"]}) \n {final_df.iat[i,10]}',node_list[pred_4]["value"],node_list[current_node]["value"])
            if self.isnan(pred_5) == False and pred_5 !="INIT":
                self.edge_creation(f'A{current_node}(D) \n {final_df.iat[i,2]},{final_df.iat[i,3]} ({node_list[pred_5]["time"]}) \n {final_df.iat[i,10]}',node_list[pred_5]["value"],node_list[current_node]["value"])
    
    def networkX_node_creation(self, final_df):
        self.Qode_graph.add_node('E0')
        for i in final_df["node"]:
            self.Qode_graph.add_node(f'E{i}')
             
            
    def networkX_edge_creation(self, final_df):
        self.Qode_graph.add_edge('E0', 'E1', weight= [final_df.iat[0,2],2,'A1'])
        for i in range(0, final_df.shape[0]):
            current_node=final_df.iat[i,0]
            current_node_no = final_df.iat[i,15]
            pred_1=final_df.iat[i,4]
            pred_2=final_df.iat[i,5]
            pred_3=final_df.iat[i,6]
            pred_4=final_df.iat[i,7]
            pred_5=final_df.iat[i,8]
            if self.isnan(pred_1)==False:
                if pred_1 == "INIT":
                    if( current_node != 1):
                        self.Qode_graph.add_edge('E1', f'E{current_node}', weight= [final_df.iat[i,2], self.criticality_mapping(final_df.iat[i,9]),f'A{final_df.iat[i,0]}'])
                else:
                    node_no = final_df.loc[final_df['S#'] == pred_1, 'node'].iloc[0]
                    self.Qode_graph.add_edge(f'E{node_no}', f'E{current_node_no}', weight= [final_df.iat[i,2], self.criticality_mapping(final_df.iat[i,9]),f'A{final_df.iat[i,0]}'])
            if self.isnan(pred_2)==False and pred_2 !="INIT":
                node_no = final_df.loc[final_df['S#'] == pred_2, 'node'].iloc[0]
                self.Qode_graph.add_edge(f'E{node_no}', f'E{current_node_no}', weight= [final_df.iat[i,2], self.criticality_mapping(final_df.iat[i,9]),f'A{final_df.iat[i,0]}(A)'])
            if self.isnan(pred_3)== False and pred_3 !="INIT":
                node_no = final_df.loc[final_df['S#'] == pred_3, 'node'].iloc[0]
                self.Qode_graph.add_edge(f'E{node_no}', f'E{current_node_no}', weight= [final_df.iat[i,2], self.criticality_mapping(final_df.iat[i,9]),f'A{final_df.iat[i,0]}(B)'])
            if self.isnan(pred_4) == False and pred_4 !="INIT":
                node_no = final_df.loc[final_df['S#'] == pred_4, 'node'].iloc[0]
                self.Qode_graph.add_edge(f'E{node_no}', f'E{current_node_no}', weight= [final_df.iat[i,2], self.criticality_mapping(final_df.iat[i,9]),f'A{final_df.iat[i,0]}(C)'])
            if self.isnan(pred_5) == False and pred_5 !="INIT":
                node_no = final_df.loc[final_df['S#'] == pred_5, 'node'].iloc[0]
                self.Qode_graph.add_edge(f'E{node_no}', f'E{current_node_no}', weight= [final_df.iat[i,2], self.criticality_mapping(final_df.iat[i,9]),f'A{final_df.iat[i,0]}(D)'])

    def find_leafnodes(self, G):
        leafnode = []

        for i in G.nodes:
            head =  []
            if nx.descendants(G, i) == set(): 
                for a in nx.ancestors(G, i):  
                    if nx.ancestors(G, a) == set():  
                        head.append(a)
            if len(head) == 1: 
                leafnode.append(i)
        return leafnode
    
    def new_avg_criticality(self, path):
        path_length = len(path) - 1
        total = 0
        for i in range(0,path_length):
            critical_value = self.Qode_graph.get_edge_data(path[i],path[i+1])["weight"][1]
            total =  total + critical_value
        return (total/path_length)
    
    def node_to_edge(self, path):
        result = []
        for i in range(0,len(path)-1):
            result.append(self.Qode_graph.get_edge_data(path[i],path[i+1])["weight"][2])
        return result
    
    def find_critical_paths(self, final_df, node_list):
        # Find the leaf nodes
        leaf_node = self.find_leafnodes(self.Qode_graph)
        
        #Segregate if the node is Material
        material_leaf_node = []
        for i in leaf_node:
            temp = final_df.loc[final_df['node'] == int(i[1:]), 'Output type'].iloc[0]
            if temp.lower() == "material":
                material_leaf_node.append(i)
                
        # Find the maximum time of the leaf nodes
        max_time = 0
        for i in material_leaf_node:
            i = int(i[1:])
            j = final_df.loc[final_df['node'] == i, 'S#'].iloc[0]
            if node_list[j]["time"] > max_time:
                max_time = node_list[j]["time"]
        
        release_time = math.ceil(max_time)
        
                
        # Select the nodes having the maximum time
        final_leaf_node = []
        for i in material_leaf_node:
            j = final_df.loc[final_df['node'] == int(i[1:]), 'S#'].iloc[0]
            if node_list[j]["time"] == max_time:
                final_leaf_node.append(i)
                
        # Find all the paths having the same node as final node
        paths_list = []
        for node in final_leaf_node:
            paths = sorted(nx.all_simple_paths(self.Qode_graph, source= 'E0', target= node))
            paths_list = paths_list + paths
            
        # Find all the paths having maximum time
        max_time_path_list = []
        for path in paths_list:
            len_path = 0
            for i in range(0,len(path)-1):
                len_path = len_path + self.Qode_graph.get_edge_data(path[i],path[i+1])["weight"][0]
            if len_path == max_time:
                max_time_path_list.append(path)
                
        # Find all the avg criticality and segregate it with the maximum value
        critical_list = []
        for i in max_time_path_list:
            critical_list.append(self.new_avg_criticality(i))
        max_avg_criticality = max(critical_list)
        avg_criticality = round(max_avg_criticality,3)
        
        max_critical_path_list = []
        for i in range(0,len(critical_list)):
            if max_avg_criticality == critical_list[i]:
                max_critical_path_list.append(max_time_path_list[i])
        
        # Select the paths with the maximum length
        max_length = 0
        critical_path = 0
        temp_list = []
        for item in max_critical_path_list:
            if len(item) > max_length:
                max_length = len(item)
        
        for item in max_critical_path_list:
            if len(item) == max_length:
                critical_path = item
                temp_list.append(item)
        temp_list
        final_critical_list = []
        for item in temp_list:
            final_critical_list.append(self.node_to_edge(item))
        
        return final_critical_list
        
    def output(self, final_critical_list):
        
        output_file_png = "Network_Diagram.png"
        output_file_svg = "Network_Diagram.svg"
        self.dot_graph.write_raw("Diagram_Network")
        #self.dot_graph.write_png(output_file_png)
        #self.dot_graph.write_svg(output_file_svg)

     
    def create_network_diagram(self):
        #df = io.BytesIO(uploaded['Sample-QODE-Questionnaire.xlsm'])
        df = 'QODE-Questionnaire.xlsm'
        data_read = pd.read_excel(df, sheet_name="Q_Stories", header=3)[2:]
        #Let us Create an object 
        logger=logging.getLogger() 

        #Now we are going to Set the threshold of logger to DEBUG 
        logger.setLevel(logging.DEBUG) 
        logger.debug("creating_process_network_diagram")
        logger.debug("data_read is done")
        logger.debug(data_read)
        Semi_Final_df = data_read[data_read['Yes / No'] == 'Yes']
        column = Semi_Final_df.columns.tolist()
        for i in range(0,len(column)):
            column[i] = column[i].lower()   
        selected_columns = ["S#","Yes / No","Total time taken","Manual time spent","Predecessor 1 (incl. INIT)","Predecessor 2 (optional)","Predecessor 3 (optional)","Predecessor 4 (optional)","Predecessor 5 (optional)","Criticality","Team / owner role","Input","Output","Automation tool","Output type"]
        flag = 0
        for item in selected_columns:
            if item.lower() not in column:
                error = f'The Column "{item}" is not found in your data sheet'
                messagebox.showerror(title= "ERROR", message= error)
                flag = 1
                break
        if flag == 0:
            final_columns = Semi_Final_df[selected_columns]
            final_df = final_columns.copy()
            temp_arr = []
            for i in range(1,final_df.shape[0]+1):
                temp_arr.append(i)
            final_df['node'] = temp_arr
            self.pydot_node_creation(final_df)
            self.calculate_lead_time(final_df, self.node_list)
            self.pydot_edge_creation(final_df, self.node_list)
            self.networkX_node_creation(final_df)
            self.networkX_edge_creation(final_df)
            critical_path_list = self.find_critical_paths(final_df, self.node_list)
            self.output(critical_path_list)

if __name__ == "__main__":
  uac = Process_Diagram()
  uaac = uac.create_network_diagram()      