# #!/usr/bin/env python3
# from tkinter import *
# from PIL import Image, ImageTk

# class Later_UI(Frame):
#     def __init__(self, master):
#         Frame.__init__(self, master)
#         self.master = master
#         self.initUI()


#     def initUI(self):
#         def _create_circle(self, x, y, r, **kwargs):
#             return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)
#         self.master.title("WiFi Positioning")
#         self.pack(fill=BOTH, expand=1)
#         self.map = ImageTk.PhotoImage(Image.open("data/images/map_modded.png"))
#         self.layer = Canvas(self, width=1200, height=1023)
#         self.layer.create_circle = _create_circle
#         self.layer.create_image(0, 0, anchor=NW, image=self.map)
#         self.layer.pack(fill=BOTH, expand=1)

#     def drawPos(self,rssi_vec,dist_vec):
#         def color_select(sig):
#             if sig > -40:
#                 color = "#00FF00"
#             elif sig <= -40 and sig > -50:
#                 color = "#90FF00"
#             elif sig <= -50 and sig > -60:
#                 color = "#FFFF00"
#             elif sig <= -60 and sig > -70:
#                 color = "#FF9933"
#             elif sig <= -70 and sig > -80:
#                 color = "#FF5333"
#             elif sig <= -80:
#                 color = "#FF0000"
#             return color
#         self.agent = ImageTk.PhotoImage(Image.open("data/images/agent.png"))
#         self.layer.delete("rad")
#         self.layer.delete("agnt")
#         ap_cords = [[400, 280],[440,810],[1050,220]]
#         for mac,dist in dist_vec.items():
#             for idx in range(len(dist)):
#                 if rssi_vec[idx] != -200:
#                     self.layer.create_circle(self.layer,ap_cords[idx][0], ap_cords[idx][1],\
#                                         dist[idx]*30.1, outline=color_select(rssi_vec[idx]),\
#                                         width=5,tags="rad")
#                     self.layer.pack(fill=BOTH, expand=1)
#         self.layer.create_image(370, 150, anchor=NW, image=self.agent,tags="agnt")
#         self.layer.create_text(350, 175, anchor=NW, text="Real position",tags="agnt")
#         # self.layer.create_image(450, 360, anchor=NW, image=self.agent,tags="agnt")
#         # self.layer.create_text(430, 385, anchor=NW, text="Real position",tags="agnt")
