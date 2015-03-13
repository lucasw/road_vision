/*
  Lucas Walter
  March 2015

  GPL 3.0

  
  Have a network of roads with cars moving along them

  g++ road_net.cpp -lopencv_highgui -lopencv_core && ./a.out
*/

#include <iostream>
#include <opencv2/highgui/highgui.hpp>
#include <map>
#include <vector>

class Edge;
// an intersection
class Node
{
public:
  Node(cv::Point2f pos);
  
  void draw(cv::Mat& image);

  // TBD or just all connections mixed?
  std::vector<Edge*> inputs_;
  std::vector<Edge*> outputs_;
  
  const cv::Point2f pos_;
};

Node::Node(cv::Point2f pos) :
    pos_(pos)
{
   
}

void Node::draw(cv::Mat& image)
{
  cv::Scalar col = cv::Scalar(255, 240, 10);
  cv::circle(image, pos_, 4, col, 2); 
}

class Edge
{
public:
  Edge(Node* start, Node* end, cv::Scalar col);
  
  void draw(cv::Mat& image);
  
  float length_;
  Node* start_;
  Node* end_;
  cv::Scalar col_;
};

Edge::Edge(Node* start, Node* end, const cv::Scalar col) :
    start_(start),
    end_(end),
    col_(col)
{
  start_->outputs_.push_back(this);
  end_->inputs_.push_back(this);
  
  const float dx = end_->pos_.x - start_->pos_.x;
  const float dy = end_->pos_.y - start_->pos_.y;
  length_ = std::sqrt( dx * dx + dy * dy ); 
}


void Edge::draw(cv::Mat& image)
{
  cv::Point2f ap = start_->pos_;
  cv::Point2f bp = end_->pos_;
  cv::Point2f mid = ap + (bp - ap) * 0.7; 
  cv::line(image, ap, mid, col_, 2); 
  cv::line(image, mid, bp, col_ * 0.5, 2); 
}

class Car
{
public:
  Car() {}

  void draw(cv::Mat& image);
  void update();

  Edge* cur_edge_;
  float progress_;
};

void Car::draw(cv::Mat& image)
{
  cv::Point2f ap = cur_edge_->start_->pos_;
  cv::Point2f bp = cur_edge_->end_->pos_;
  cv::Point2f mid = ap + (bp - ap) * (progress_ / cur_edge_->length_); 
  
  cv::circle(image, mid, 10, cv::Scalar(200,200,200), -1); 
}

void Car::update()
{
  progress_ += 0.5;
  
  if (progress_ > cur_edge_->length_)
  {
    cur_edge_ = cur_edge_->end_->outputs_[rand() % cur_edge_->end_->outputs_.size()];
    progress_ = 0;
  }
}

///////////////////////////////////////////////////////////////////////////////
int main(int argn, char** argv)
{
  const int wd = 1280;
  const int ht = 720;
  
  cv::Mat image = cv::Mat(cv::Size(wd, ht), CV_8UC3, cv::Scalar::all(0));

  std::vector<Node*> all_nodes;
  std::vector<Edge*> all_edges;

  const float div = 128.0;
  const float off = 24.0;
  const int x_num = float(wd)/div;
  const int y_num = float(ht)/div;
  for (size_t j = 0; j < y_num; ++j)
  {
    for (size_t i = 0; i < x_num; ++i)
    {
      // create an intersection
      const float x = i * div + div/2.0 - off/2.0;
      const float y = j * div + div/2.0 + off/2.0;
      all_nodes.push_back(new Node(cv::Point2f(x, y))); 
      
      if (i > 0)
      { 
        // to the west
        size_t ind1 = j * x_num * 4 + i * 4; //all_nodes.size() - 1;
        size_t ind2 = j * x_num * 4 + (i - 1) * 4 + 1;
        cv::Scalar col = cv::Scalar(255, 100, 50);
        all_edges.push_back(new Edge(all_nodes[ind1], all_nodes[ind2], col));
      }
      if (j > 0)
      { 
        // to the south
        size_t ind1 = (j - 1) * x_num * 4 + i * 4 + 3; //all_nodes.size() - 1;
        size_t ind2 = j * x_num * 4 + i * 4;
        cv::Scalar col = cv::Scalar(105, 150, 190);
        all_edges.push_back(new Edge(all_nodes[ind1], all_nodes[ind2], col));
      }


      all_nodes.push_back(new Node(cv::Point2f(x + off, y)));

      if (j > 0)
      { 
        // to the north
        size_t ind1 = j * x_num * 4 + i * 4 + 1; //all_nodes.size() - 1;
        size_t ind2 = (j - 1) * x_num * 4 + i * 4 + 2;
        cv::Scalar col = cv::Scalar(145, 150, 90);
        all_edges.push_back(new Edge(all_nodes[ind1], all_nodes[ind2], col));
      }

      all_nodes.push_back(new Node(cv::Point2f(x + off, y + off))); 
      all_nodes.push_back(new Node(cv::Point2f(x, y + off))); 
    
      if (i > 0)
      { 
        // to the east
        size_t ind2 = j * x_num * 4 + i * 4 + 3; //all_nodes.size() - 1;
        size_t ind1 = j * x_num * 4 + (i - 1) * 4 + 2;
        cv::Scalar col = cv::Scalar(105, 250, 50);
        all_edges.push_back(new Edge(all_nodes[ind1], all_nodes[ind2], col));
      }
      
      // connections within intersection
      {
        size_t ind = j * x_num * 4 + i * 4 ;
        // to the east
        all_edges.push_back(new Edge(all_nodes[ind + 3], all_nodes[ind + 2], 
            cv::Scalar(105, 250, 150) ));
        // to the west
        all_edges.push_back(new Edge(all_nodes[ind + 1], all_nodes[ind], 
            cv::Scalar(105, 250, 150) ));
        // to the north
        all_edges.push_back(new Edge(all_nodes[ind + 2], all_nodes[ind + 1], 
            cv::Scalar(105, 250, 150) ));
        // to the south
        all_edges.push_back(new Edge(all_nodes[ind], all_nodes[ind + 3], 
            cv::Scalar(105, 250, 150) ));

      }
    }
  }
  std::cout << x_num << " " << y_num << " " 
      << all_nodes.size() << " " << all_edges.size() << std::endl;

  Car* car = new Car();
  car->cur_edge_ = all_edges[rand() % all_edges.size()];

  while (true) 
  {
    image = cv::Scalar::all(0);
    for (size_t i = 0; i < all_edges.size(); ++i)
    {
      all_edges[i]->draw(image);
    }
 
    for (size_t i = 0; i < all_nodes.size(); ++i)
    {
      all_nodes[i]->draw(image);
    }

    car->update();
    car->draw(image);


    cv::imshow("road network", image);
    const int key = cv::waitKey(20);
    if (key == 'q') break;
  }


}

