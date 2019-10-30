import numpy as np
import plotly
import plotly.graph_objects as go


class DeepRacerTrack:
    def __init__(self, df, track_name):
        self.df = df
        self.track_name = track_name
        self.episodes_per_iteration = df[df['iteration']==1]['episode'].max()+1
        self.center_line, self.inner_border, self.outer_border = self.load_track(track_name)
        self.tmin, self.tmax = self.get_throttle_minmax(df)
    
    def load_track(self, track_name, absolute_path="."):
        if track_name.endswith('.npy'):
            track_name = track_name[:-4]
        waypoints = np.load("%s/tracks/%s.npy" % (absolute_path, track_name))
        # rescale waypoints to centimeter scale
        center_line = waypoints[:, 0:2] * 100
        inner_border = waypoints[:, 2:4] * 100
        outer_border = waypoints[:, 4:6] * 100
        return center_line, inner_border, outer_border 
        
    def get_throttle_minmax(self, df):
        tmax = 0
        tmin = 100
        for i in range(self.episodes_per_iteration):
            episode_data = df[df['episode'] == i]
            tmin=min(tmin, episode_data["throttle"][1:].min())
            tmax=max(tmax, episode_data["throttle"].max())
        return tmin, tmax
    
    def plot_track(self):
        fig = go.Figure()
        self.plot_track_(fig)
        fig.show()
        
    def plot_track_(self, fig):
        fig.add_trace(go.Scatter(x=self.center_line[:, 0], y=self.center_line[:, 1],
                                 line = dict(color='rgb(190,190,190)', width=2), mode='lines+markers',
                                    hovertext=["Waypoint: {}<br>Location: ({:.2f}, {:.2f})".format(
                                        i, self.center_line[i, 0], self.center_line[i, 1]) 
                                               for i in range(len(self.center_line))],
                                    hoverinfo="text"))
        fig.add_trace(go.Scatter(x=[self.center_line[i, 0] for i in range(0, len(self.center_line), 10)], 
                                 y=[self.center_line[i, 1] for i in range(0, len(self.center_line), 10)],
                                 line = dict(color='rgb(100,100,100)', width=4), mode='markers',
                                    hovertext=["Waypoint: {}<br>Location: ({:.2f}, {:.2f})".format(
                                        i, self.center_line[i, 0], self.center_line[i, 1]) 
                                               for i in range(0, len(self.center_line), 10)],
                                    hoverinfo="text"))
        fig.add_trace(go.Scatter(x=self.inner_border[:, 0], y=self.inner_border[:, 1], 
                                 line = dict(color='rgb(100,200,100)', width=3), mode='lines'))
        fig.add_trace(go.Scatter(x=self.outer_border[:, 0], y=self.outer_border[:, 1],  
                                 line = dict(color='rgb(100,200,100)', width=3), mode='lines'))
        fig.update_layout(
            width = 900,
            height = 700,
            title = "Interactive Racing Track",
            xaxis=dict(
              showgrid=False,
              zeroline=False,
            ),
            yaxis = dict(
              scaleanchor = "x",
              scaleratio = 1,
              showgrid=False,
              zeroline=False
            ),
            showlegend=False,
            annotations=[go.layout.Annotation(
                    x=self.center_line[i, 0],
                    y=self.center_line[i, 1],
                    xref="x",
                    yref="y",
                    text=i,
                    showarrow=True,
                    arrowhead=0,
                    ax=10,
                    ay=-20
                ) for i in range(0, len(self.center_line), 10)]
        )
        
    def plot_episode(self, episode):
        fig = go.Figure()
        self.plot_track_(fig)
        self.plot_episode_(fig, episode)
        fig.show()
        
    def plot_episode_(self, fig, episode, showscale=True):
        episode_data = self.df[self.df['episode'] == episode]
        fig.add_trace(go.Scatter(
            x=episode_data["x"], 
            y=episode_data["y"], 
            line = dict(color='rgb(200,100,100)', width=5), 
            mode='lines+markers',
            marker=dict(size=8,
                        cmin=self.tmin,
                        cmax=self.tmax,
                        showscale=showscale,
                        colorbar=dict(
                            title="Throttle"
                        ),
                        color=episode_data["throttle"],
                        colorscale="Plasma"),
            hovertext=["Iteration: {}<br>Episode: {}<br>Steps: {}<br>Progress: {:.2f}<br>Action: {}<br>Throttle: {}<br>Steer: {:.1f}<br>Reward: {}<br>Closest WP: {}".format(
                episode_data.iloc[i]["iteration"],
                episode_data.iloc[i]["episode"], 
                episode_data.iloc[i]["steps"], 
                episode_data.iloc[i]["progress"], 
                episode_data.iloc[i]["action"], 
                episode_data.iloc[i]["throttle"], 
                episode_data.iloc[i]["steer"]*180/np.pi, 
                episode_data.iloc[i]["reward"], 
                episode_data.iloc[i]["closest_waypoint"]) 
                       for i in range(len(episode_data))],
            hoverinfo="text"))
    
    def plot_iteration(self, iteration):
        fig = go.Figure()
        self.plot_iteration_(fig, iteration)
        fig.show()
        
    def plot_iteration_(self, fig, iteration):
        self.plot_track_(fig)
        for i in range((iteration-1)*self.episodes_per_iteration, (iteration)*self.episodes_per_iteration):
            if (i%self.episodes_per_iteration)==0:
                self.plot_episode_(fig, i, True)
            else:
                self.plot_episode_(fig, i, False)