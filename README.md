# laserify
Laserify converts CNC g-code to laser compatible g-code and does a little bit of g-code cleanup.

#### Options

You can pass the following options to the program:

<table class="table" width="100%">
<thead>
  <tr>
    <th width="20%">Option</th>
    <th width="80%">Description</th>
  </tr>
  <tr>
    <td><code>-h, --help</code></td>
    <td>shows help information</td>
  </tr>
  <tr>
    <td><code>-o, --outfile</code></td>
    <td>outfile, for processed g-code, otherwise using STDOUT</td>
  </tr>
  <tr>
    <td><code>-z, --zero</code></td>
    <td>zeros all Z-direction moves, otherwise, z-moves are kept as is (except that pure z-moves without X or Y movement are done with laser turned off) </td>
  </tr>
  <tr>
    <td><code>-lon, --laser-on</code></td>
    <td>g-code to turn laser on (defaults to 'M3')</td>
  </tr>
  <tr>
    <td><code>-loff, --laser-off</code></td>
    <td>g-code to turn laser off (defaults to 'M5')</td>
  </tr>
 </tbody>
</table>

Laserify needs Python3 to run. It is a command line program and works on Windows, Linux and OSX.

#### Disclaimer
Laser are dangerous - always were eye protection and keep your cat at a safe distance! I assume no responsibility of any kind for running the g-code this program produces.
