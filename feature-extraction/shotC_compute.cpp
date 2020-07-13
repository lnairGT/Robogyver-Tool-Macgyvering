#include <iostream>
#include <pcl/io/ply_io.h>
#include <pcl/point_types.h>
#include <pcl/features/shot.h>
#include <pcl/features/normal_3d.h>
#include <pcl/visualization/pcl_plotter.h>
#include <pcl/keypoints/sift_keypoint.h>
#include <pcl/common/centroid.h>
#include <pcl/visualization/pcl_visualizer.h>
#include <pcl/common/transforms.h>
#include <pcl/common/pca.h>
#include <pcl/common/common.h>
#include <fstream>
#include <string.h>
#include <stdlib.h>
#include <dirent.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/types.h>


using namespace std;

void SHOTC_compute(pcl::PointCloud<pcl::SHOT352>::Ptr descriptors, pcl::PointCloud<pcl::PointXYZ>::Ptr input_cloud, float radius, pcl::PointXYZ c)
{
	// Compute SHOT-C features
	
    pcl::PointCloud<pcl::Normal>::Ptr normals(new pcl::PointCloud<pcl::Normal>);
	pcl::NormalEstimation<pcl::PointXYZ, pcl::Normal> normalEstimation;
    normalEstimation.setInputCloud(input_cloud);
    normalEstimation.setRadiusSearch(radius);
    pcl::search::KdTree<pcl::PointXYZ>::Ptr kdtree(new pcl::search::KdTree<pcl::PointXYZ>());
    normalEstimation.setSearchMethod(kdtree);
    normalEstimation.compute(*normals);

    pcl::PointCloud<pcl::PointXYZ>::Ptr new_cloud(new pcl::PointCloud<pcl::PointXYZ>);
    new_cloud->push_back(c);
    pcl::SHOTEstimation<pcl::PointXYZ, pcl::Normal, pcl::SHOT352> shot;
    shot.setSearchMethod(kdtree);
    shot.setSearchSurface(input_cloud);
    shot.setInputCloud(new_cloud);
    shot.setInputNormals(normals);
    shot.setRadiusSearch(radius);
    shot.compute(*descriptors);
}

Eigen::Vector4f centroid_compute(pcl::PointCloud<pcl::PointXYZ>::Ptr input_cloud)
{
    Eigen::Vector4f pcaCentroid;
    pcl::compute3DCentroid(*input_cloud, pcaCentroid);
    return pcaCentroid;
}

float radius_compute(pcl::PointCloud<pcl::PointXYZ>::Ptr input_cloud, Eigen::Vector4f pcaCentroid)
{
    Eigen::Matrix3f covariance;
    computeCovarianceMatrixNormalized(*input_cloud, pcaCentroid, covariance);
    Eigen::SelfAdjointEigenSolver<Eigen::Matrix3f> eigen_solver(covariance, Eigen::ComputeEigenvectors);
    Eigen::Matrix3f eigenVectorsPCA = eigen_solver.eigenvectors();
    eigenVectorsPCA.col(2) = eigenVectorsPCA.col(0).cross(eigenVectorsPCA.col(1));

    Eigen::Matrix4f projectionTransform(Eigen::Matrix4f::Identity());
    projectionTransform.block<3,3>(0,0) = eigenVectorsPCA.transpose();
    projectionTransform.block<3,1>(0,3) = -1.f * (projectionTransform.block<3,3>(0,0) * pcaCentroid.head<3>());
    
    pcl::PointCloud<pcl::PointXYZ>::Ptr cloudPointsProjected (new pcl::PointCloud<pcl::PointXYZ>);
    pcl::transformPointCloud(*input_cloud, *cloudPointsProjected, projectionTransform);

    pcl::PointXYZ minPoint;
    pcl::PointXYZ maxPoint;
    pcl::getMinMax3D(*cloudPointsProjected, minPoint, maxPoint);
    const Eigen::Vector3f meanDiagonal = 0.5f*(maxPoint.getVector3fMap() + minPoint.getVector3fMap());

    float x, y, z;

    x = maxPoint.x - minPoint.x;
    y = maxPoint.y - minPoint.y;
    z = maxPoint.z - minPoint.z;

    float radius = 0;
    
    if(x>y)
    {
        radius = x;
    }
    else
    {
        radius = y;
    }
    
    if(z>radius)
    {
        radius = z;
    }

    return radius;
}

int main(int argc, char** argv)
{
	ofstream shotc_file;
	shotc_file.open("ShotC_descriptors_attachment.csv");

	shotc_file << "Name" << ",";
	for (int i = 1; i <= 352; i++)
	{
		shotc_file << "Feature" << i << ",";
	}

	shotc_file << "\n";

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

			if (pcl::io::loadPLYFile<pcl::PointXYZ> (filepath, *cloud) == -1)
			{
				PCL_ERROR("Couldn't read PLY file \n");
				continue;
			}

            shotc_file << pcl_name << ",";
			cout << pcl_name << endl;

            // Compute centroid
            Eigen::Vector4f pcaCentroid;
            pcl::PointXYZ c;

            pcaCentroid = centroid_compute(cloud);
            c.x = pcaCentroid[0];
            c.y = pcaCentroid[1];
            c.z = pcaCentroid[2];

            // Compute SHOT estimation radius
            float radius = radius_compute(cloud, pcaCentroid);

            // Compute SHOT-C features
			SHOTC_compute(descriptors, cloud, radius, c);
            for(int m=0;m<352;m++)
            {
                shotc_file<<descriptors->points[0].descriptor[m]<<",";
            }
            shotc_file<<"\n";

		}
		closedir(dir);
	}
	else
	{
		cout << "Couldn't open directory" << endl;
	}

	shotc_file.close();
	return 0;
}
