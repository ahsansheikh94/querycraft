import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  Plus, 
  Database, 
  FileText, 
  Clock, 
  Search,
  ArrowRight,
  FolderOpen,
  BarChart3
} from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import Header from '../../components/layout/Header';
import { Project, Query } from '../../types';
import apiService from '../../lib/api';
import { formatDate } from '../../lib/utils';
import toast from 'react-hot-toast';

export default function DashboardPage() {
  const [searchQuery, setSearchQuery] = useState('');

  // Fetch projects
  const { data: projectsData, isLoading: projectsLoading } = useQuery({
    queryKey: ['projects'],
    queryFn: () => apiService.getProjects(1, 10),
  });

  // Fetch recent queries (we'll get this from the first project for demo)
  const { data: recentQueries, isLoading: queriesLoading } = useQuery({
    queryKey: ['recent-queries'],
    queryFn: async () => {
      if (projectsData?.data.length > 0) {
        try {
          const queryData = await apiService.getQueries(projectsData.data[0].id, 1, 5);
          return queryData.data;
        } catch (error) {
          return [];
        }
      }
      return [];
    },
    enabled: !!projectsData?.data.length,
  });

  const filteredProjects = projectsData?.data.filter(project =>
    project.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    project.description?.toLowerCase().includes(searchQuery.toLowerCase())
  ) || [];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  return (
    <div className="min-h-screen">
      <Header 
        onSearch={setSearchQuery}
        showSearch={true}
        showCreateButton={true}
      />
      
      <main className="container mx-auto px-4 py-8">
        {/* Welcome Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold gradient-text mb-2">
            Welcome to QueryCraft
          </h1>
          <p className="text-muted-foreground text-lg">
            Transform your natural language into powerful SQL queries
          </p>
        </motion.div>

        {/* Stats Cards */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8"
        >
          <motion.div variants={itemVariants}>
            <Card className="glass-card">
              <CardContent className="p-6">
                <div className="flex items-center space-x-4">
                  <div className="p-3 bg-emerald-500/10 rounded-lg">
                    <Database className="h-6 w-6 text-emerald-500" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold">
                      {projectsData?.data.length || 0}
                    </p>
                    <p className="text-sm text-muted-foreground">Total Projects</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div variants={itemVariants}>
            <Card className="glass-card">
              <CardContent className="p-6">
                <div className="flex items-center space-x-4">
                  <div className="p-3 bg-blue-500/10 rounded-lg">
                    <FileText className="h-6 w-6 text-blue-500" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold">
                      {recentQueries?.length || 0}
                    </p>
                    <p className="text-sm text-muted-foreground">Recent Queries</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div variants={itemVariants}>
            <Card className="glass-card">
              <CardContent className="p-6">
                <div className="flex items-center space-x-4">
                  <div className="p-3 bg-purple-500/10 rounded-lg">
                    <BarChart3 className="h-6 w-6 text-purple-500" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold">
                      {projectsData?.data.reduce((acc, project) => acc + (project.stats?.schema_count || 0), 0) || 0}
                    </p>
                    <p className="text-sm text-muted-foreground">Total Schemas</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Projects Section */}
          <motion.div
            variants={containerVariants}
            initial="hidden"
            animate="visible"
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-semibold">Your Projects</h2>
              <Link to="/projects/new">
                <Button className="gradient">
                  <Plus className="h-4 w-4 mr-2" />
                  New Project
                </Button>
              </Link>
            </div>

            {projectsLoading ? (
              <div className="space-y-4">
                {[1, 2, 3].map((i) => (
                  <Card key={i} className="glass-card">
                    <CardContent className="p-6">
                      <div className="animate-pulse">
                        <div className="h-4 bg-white/10 rounded w-3/4 mb-2"></div>
                        <div className="h-3 bg-white/10 rounded w-1/2"></div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : filteredProjects.length === 0 ? (
              <Card className="glass-card">
                <CardContent className="p-8 text-center">
                  <FolderOpen className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-semibold mb-2">No projects yet</h3>
                  <p className="text-muted-foreground mb-4">
                    Create your first project to start generating SQL queries
                  </p>
                  <Link to="/projects/new">
                    <Button className="gradient">
                      <Plus className="h-4 w-4 mr-2" />
                      Create Project
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            ) : (
              <motion.div variants={containerVariants} className="space-y-4">
                {filteredProjects.map((project, index) => (
                  <motion.div key={project.id} variants={itemVariants}>
                    <Link to={`/project/${project.id}`}>
                      <Card className="glass-card hover:bg-white/5 transition-colors cursor-pointer">
                        <CardContent className="p-6">
                          <div className="flex items-center justify-between">
                            <div className="flex-1">
                              <h3 className="text-lg font-semibold mb-1">{project.name}</h3>
                              <p className="text-sm text-muted-foreground mb-2">
                                {project.description || 'No description'}
                              </p>
                              <div className="flex items-center space-x-4 text-xs text-muted-foreground">
                                <span>{project.stats?.schema_count || 0} schemas</span>
                                <span>{project.stats?.query_count || 0} queries</span>
                                <span>{formatDate(project.updated_at)}</span>
                              </div>
                            </div>
                            <ArrowRight className="h-5 w-5 text-muted-foreground" />
                          </div>
                        </CardContent>
                      </Card>
                    </Link>
                  </motion.div>
                ))}
              </motion.div>
            )}

            {filteredProjects.length > 0 && (
              <div className="mt-6 text-center">
                <Link to="/projects">
                  <Button variant="outline">
                    View All Projects
                  </Button>
                </Link>
              </div>
            )}
          </motion.div>

          {/* Recent Queries Section */}
          <motion.div
            variants={containerVariants}
            initial="hidden"
            animate="visible"
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-semibold">Recent Queries</h2>
              <Link to="/queries">
                <Button variant="outline" size="sm">
                  View All
                </Button>
              </Link>
            </div>

            {queriesLoading ? (
              <div className="space-y-4">
                {[1, 2, 3].map((i) => (
                  <Card key={i} className="glass-card">
                    <CardContent className="p-4">
                      <div className="animate-pulse">
                        <div className="h-3 bg-white/10 rounded w-full mb-2"></div>
                        <div className="h-3 bg-white/10 rounded w-3/4"></div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : recentQueries?.length === 0 ? (
              <Card className="glass-card">
                <CardContent className="p-8 text-center">
                  <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-semibold mb-2">No queries yet</h3>
                  <p className="text-muted-foreground">
                    Generate your first SQL query from natural language
                  </p>
                </CardContent>
              </Card>
            ) : (
              <motion.div variants={containerVariants} className="space-y-4">
                {recentQueries?.map((query, index) => (
                  <motion.div key={query.id} variants={itemVariants}>
                    <Card className="glass-card">
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <p className="text-sm font-medium mb-1 line-clamp-2">
                              {query.user_input}
                            </p>
                            <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                              <Clock className="h-3 w-3" />
                              <span>{formatDate(query.created_at)}</span>
                            </div>
                          </div>
                          <Link to={`/query/${query.id}`}>
                            <Button variant="ghost" size="sm">
                              <ArrowRight className="h-4 w-4" />
                            </Button>
                          </Link>
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                ))}
              </motion.div>
            )}
          </motion.div>
        </div>
      </main>
    </div>
  );
}
