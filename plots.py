import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
import numpy as np
import pyqtgraph.opengl as gl
from misc_functions import WaveGenerator


class SignalPlot(pg.PlotWidget):
    """
    This class is a simple wrapper around the pg.PlotWidget to capture keypresses
    when the plot is the active widget.
    """
    keyPressed = QtCore.pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.line_width = 1
        self.curve_colors = ['b', 'g', 'r', 'c', 'y', 'm']
        self.pens = [pg.mkPen(i, width=self.line_width) for i in self.curve_colors]

        self.setFocusPolicy(QtCore.Qt.StrongFocus)  # By default the plot is the keyboard focus
        self.showGrid(y=True)

        self.disableAutoRange('y')

    def keyPressEvent(self, event):
        """ When a key is pressed, pass it up to the PyQt event handling system. """
        super().keyPressEvent(event)
        self.keyPressed.emit(event.key())

    def on_new_data_update_plot(self, incomingData):
        """ Each time the thread sends data, plot every row as a new line."""
        self.clear()  # Clear last update's lines
        for i in range(0, np.shape(incomingData)[0]):  # For each row in incomingData
            # Plot all rows
            self.plot(incomingData[i], clear=False, pen=self.pens[i])


class ThreeDPlot(gl.GLViewWidget):
    """
    Creates an OpenGL 3D plot for pseudo-viewing of the magnetic field.

    """

    def __init__(self, funcg_rate, writechunksize, vmulti, freq, camber, zphase):
        super().__init__()

        # Instantiate wave generator
        self.WaveGen = WaveGenerator()
        # Set up plot, add white background grids
        self.gridsize = 10
        gridx = gl.GLGridItem()
        gridx.translate(0, 0, -2)
        self.addItem(gridx)

        # self.opts['distance'] = 40

        gaxis = gl.GLAxisItem()
        gaxis.setSize(x=3, y=3, z=3)
        self.addItem(gaxis)
        self.orbit(234, -5)  # Sets default view position
        self.setBackgroundColor('k')

        # Initialize signal design variables
        self.funcg_rate = funcg_rate
        self.writechunksize = writechunksize
        self.vmulti = vmulti
        self.freq = freq
        self.camber = camber
        self.zphase = zphase

        self.pts = self.WaveGen.generate_waves(
            funcg_rate=self.funcg_rate,
            writechunksize=self.writechunksize,
            vmulti=self.vmulti,
            freq=self.freq,
            camber=self.camber,
            zphase=self.zphase,
            zcoeff=1)

        # Plot first circle
        self.last_update = 0.1
        self.plot_data(firstrun=True)

    def plot_data(self, firstrun=False):
        """
        On a change in signal design properties, plot a new circle.
        """
        # Timing
        now = pg.ptime.time()
        time_elapsed = now - self.last_update

        if time_elapsed < 0.07:  # Basically, if a bunch of changes are made fast, skip plotting
            pass
        else:  # Continue along and plot
            self.last_update = now
            # print(time_elapsed)

            if firstrun is not True:
                for i, e in enumerate(self.last_lines):
                    self.removeItem(self.last_lines[i])

            self.pts = self.WaveGen.generate_waves(
                funcg_rate=self.funcg_rate,
                writechunksize=self.writechunksize,
                vmulti=self.vmulti,
                freq=10,
                camber=self.camber,
                zphase=self.zphase,
                zcoeff=1)

            # Plot 4 line segments, two of which are blue.
            self.last_lines = []  # To clear previous lines when a new circle is plotted
            self.colors = ['g', 'r', 'b', 'b']
            pts_len = self.pts.shape[1]  # How many points
            n_segments = 4
            j = pts_len // n_segments
            for index, i in enumerate(np.arange(start=0, stop=pts_len, step=j)):
                #  Plot separate color lines
                j = i + j
                line = gl.GLLinePlotItem(pos=self.pts[:, i:j].transpose(), color=pg.glColor(self.colors[index]),
                                         width=5, antialias=True)
                self.addItem(line)
                self.last_lines.append(line)

            # Plot a cone
            # cone_mesh_data = gl.MeshData.cylinder(10, 10, radius=[0.01, 0.5], length=1)
            # cone = gl.GLMeshItem(meshdata=cone_mesh_data, color=pg.glColor('c'), edgeColor=pg.glColor('w'))
            # cone.translate(0, 5, 0)
            # cone.rotate(45, 0, 0, 0, local=True)
            # self.addItem(cone)
            # self.last_lines.append(cone)