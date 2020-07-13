#include <iostream>
#include <pcl/io/ply_io.h>
#include <pcl/point_types.h>
#include <pcl/features/shot.h>
#include <pcl/features/normal_3d.h>
#include <pcl/visualization/pcl_plotter.h>
#include <pcl/keypoints/sift_keypoint.h>
#include <pcl/common/centroid.h>
#include <pcl/visualization/pcl_visualizer.h>
#include <fstream>
#include <dirent.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/types.h>

using namespace std;

void SHOTA_compute(pcl::PointCloud<pcl::SHOT352>::Ptr descriptors, pcl::PointCloud<pcl::PointXYZ>::Ptr input_cloud)
{
	// Compute SHOT-A features
	//pcl::PointCloud<pcl::SHOT352>::Ptr descriptors(new pcl::PointCloud<pcl::SHOT352>());
	pcl::PointCloud<pcl::Normal>::Ptr normals(new pcl::PointCloud<pcl::Normal>);
	
	pcl::NormalEstimation<pcl::PointXYZ, pcl::Normal> normalEstimation;
	normalEstimation.setInputCloud(input_cloud);
	normalEstimation.setRadiusSearch(0.5);
	pcl::search::KdTree<pcl::PointXYZ>::Ptr kdtree(new pcl::search::KdTree<pcl::PointXYZ>);
	normalEstimation.setSearchMethod(kdtree);
	normalEstimation.compute(*normals);

	pcl::SHOTEstimation<pcl::PointXYZ, pcl::Normal, pcl::SHOT352> shot;
	shot.setInputCloud(input_cloud);
	shot.setInputNormals(normals);
	shot.setRadiusSearch(0.02);
	shot.compute(*descriptors);
}

int main(int argc, char** argv)
{
	ofstream shota_file;
	shota_file.open("ShotA_descriptors_attachment.csv");

	shota_file << "Name" << ",";
	for (int i = 1; i <= 352; i++)
	{
		shota_file << "Feature" << i << ",";
	}

	shota_file << "\n";

	string pcl_directory = ""; // Directory of point clouds to compute SHOT features for

	DIR *dir;
	struct dirent *ent;
	if ((dir = opendir(pcl_directory.c_str())) != NULL)
	{
		while ((ent = readdir(dir)) != NULL)
		{
			float f[352] = {0.0};
			pcl::PointCloud<pcl::PointXYZ>::Ptr cloud(new pcl::PointCloud<pcl::PointXYZ>);
			pcl::PointCloud<pcl::SHOT352>::Ptr descriptors(new pcl::PointCloud<pcl::SHOT352>());
			string pcl_name = ent->d_name;
			string filepath = pcl_directory + "/" + pcl_name;

			shota_file << pcl_name << ",";
			cout << pcl_name << endl;

			if (pcl::io::loadPLYFile<pcl::PointXYZ> (filepath, *cloud) == -1)
			{
				PCL_ERROR("Couldn't read PLY file \n");
				continue;
			}

			SHOTA_compute(descriptors, cloud);

			for (int i = 0; i < descriptors->points.size(); i++)
			{
				for (int j = 0; j < 352; j++)
				{
					f[j] += descriptors->points[i].descriptor[j];
				}
			}

			for (int i = 0; i < 352; i++)
			{
				f[i] = f[i]/(descriptors->points.size());
				if (pcl_isnan(f[i] > 0))
				{
					f[i] = 0.0;
				}
			}

			for (int i = 0; i < 352; i++)
			{
				shota_file << f[i] << ",";
			}

			shota_file << "\n"; // Last element

		}
		closedir(dir);
	}
	else
	{
		cout << "Couldn't open directory" << endl;
	}

	shota_file.close();
	return 0;
}
