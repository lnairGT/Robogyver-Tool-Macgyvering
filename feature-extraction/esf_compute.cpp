#include<iostream>
#include<vector>
#include<utility>
#include<pcl/visualization/pcl_plotter.h>
#include<pcl/features/esf.h>
#include<pcl/io/pcd_io.h>
#include<pcl/io/ply_io.h>
#include<pcl/point_types.h>
#include<pcl/visualization/pcl_visualizer.h>
#include<fstream>
#include<string.h>
#include<stdlib.h>
#include<dirent.h>
#include<stdio.h>
#include<unistd.h>
#include<sys/stat.h>
#include<sys/types.h>


using namespace std;

// the main can take in command line arguments
int main(int argc, char** argv)
{

    ofstream esf_file;
	esf_file.open("esf_descriptors_constructions.csv");

	esf_file << "Name" << ",";
	for (int i = 1; i <= 640; i++)
	{
		esf_file << "Feature" << i << ",";
	}

	esf_file << "\n";

    string pcl_directory = ""; // Directory of point clouds to compute ESF features for

	DIR *dir;
	struct dirent *ent;
	if ((dir = opendir(pcl_directory.c_str())) != NULL)
	{
		while ((ent = readdir(dir)) != NULL)
		{
			pcl::PointCloud<pcl::PointXYZ>::Ptr cloud(new pcl::PointCloud<pcl::PointXYZ>);
			pcl::ESFEstimation<pcl::PointXYZ, pcl::ESFSignature640> esf;

			string pcl_name = ent->d_name;
			string filepath = pcl_directory + "/" + pcl_name;

			if (pcl::io::loadPLYFile<pcl::PointXYZ> (filepath, *cloud) == -1)
			{
				PCL_ERROR("Couldn't read PLY file \n");
				continue;
			}

            esf_file << pcl_name << ",";
			cout << pcl_name << endl;

            esf.setInputCloud (cloud);
            pcl::PointCloud<pcl::ESFSignature640>::Ptr esfSignature (new pcl::PointCloud<pcl::ESFSignature640>);

            // Compute SHOT-C features
			esf.compute(*esfSignature);
            for(int i=0;i<640;i++)
            {
                esf_file<<float(esfSignature->points[0].histogram[i])<<",";
            }
            esf_file<<"\n";

		}
		closedir(dir);
	}
	else
	{
		cout << "Couldn't open directory" << endl;
	}

	esf_file.close();
	return 0;
}
