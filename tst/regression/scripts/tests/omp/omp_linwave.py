# Regression test based on Newtonian MHD linear wave convergence problem with OpenMP
#
# Runs a linear wave convergence test in 3D including SMR and checks L1 errors (which
# are computed by the executable automatically and stored in the temporary file
# linearwave_errors.dat)

# Modules
import os
import scripts.utils.athena as athena


# Prepare Athena++ w/wo OpenMP
def prepare(**kwargs):
    athena.configure('b', 'omp', prob='linear_wave', coord='cartesian',
                     flux='hlld', **kwargs)
    athena.make()
    os.system('mv bin/athena bin/athena_omp')

    athena.configure('b', prob='linear_wave', coord='cartesian', flux='hlld', **kwargs)
    athena.make()


# Run Athena++ w/wo OpenMP
def run(**kwargs):
    # L-going fast wave
    arguments = ['time/ncycle_out=0',
                 'problem/wave_flag=0', 'problem/vflow=0.0', 'mesh/refinement=static',
                 'mesh/nx1=32', 'mesh/nx2=16', 'mesh/nx3=16',
                 'meshblock/nx1=8',
                 'meshblock/nx2=8',
                 'meshblock/nx3=8',
                 'output2/dt=-1', 'time/tlim=2.0', 'problem/compute_error=true']
    athena.run('mhd/athinput.linear_wave3d', arguments)

    os.system('mv bin/athena_omp bin/athena')
    athena.run('mhd/athinput.linear_wave3d', arguments + ['mesh/num_threads=1'])
    athena.run('mhd/athinput.linear_wave3d', arguments + ['mesh/num_threads=2'])
    athena.run('mhd/athinput.linear_wave3d', arguments + ['mesh/num_threads=4'])


# Analyze outputs
def analyze():
    # read data from error file
    filename = 'bin/linearwave-errors.dat'
    data = []
    with open(filename, 'r') as f:
        raw_data = f.readlines()
        for line in raw_data:
            if line.split()[0][0] == '#':
                continue
            data.append([float(val) for val in line.split()])

    print(data[0][4], data[1][4], data[2][4], data[3][4])

    # check errors between runs w/wo OpenMP and different numbers of threads
    if data[0][4] != data[1][4]:
        print("Linear wave error with one OpenMP thread vs. no OpenMP not identical",
              data[0][4], data[1][4])
        return False
    if abs(data[2][4] - data[0][4]) > 5.0e-4:
        print("Linear wave error between 2 and 1 threads too large",
              data[2][4], data[0][4])
        return False
    if abs(data[3][4] - data[0][4]) > 5.0e-4:
        print("Linear wave error between 4 and 1 threads too large",
              data[2][4], data[0][4])
        return False

    return True
