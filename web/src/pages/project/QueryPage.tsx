import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  ArrowLeft, 
  Send, 
  Copy, 
  Trash2, 
  FileText,
  History,
  Sparkles,
  Save,
  RefreshCw
} from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Textarea } from '../../components/ui/textarea';
import { Label } from '../../components/ui/label';
import Header from '../../components/layout/Header';
import { Query } from '../../types';
import apiService from '../../lib/api';
import { formatDate, copyToClipboard } from '../../lib/utils';
import toast from 'react-hot-toast';

export default function QueryPage() {
  const { id: projectId } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [userInput, setUserInput] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [activeTab, setActiveTab] = useState<'generate' | 'history'>('generate');

  // Fetch project details
  const { data: project } = useQuery({
    queryKey: ['project', projectId],
    queryFn: () => apiService.getProject(projectId!),
    enabled: !!projectId,
  });

  // Fetch queries
  const { data: queriesData, isLoading } = useQuery({
    queryKey: ['queries', projectId],
    queryFn: () => apiService.getQueries(projectId!, 1, 50),
    enabled: !!projectId,
  });

  // Generate query mutation
  const generateQueryMutation = useMutation({
    mutationFn: (input: string) => apiService.generateQuery(projectId!, input),
    onSuccess: (data) => {
      toast.success('Query generated successfully!');
      queryClient.invalidateQueries({ queryKey: ['queries', projectId] });
      queryClient.invalidateQueries({ queryKey: ['project-stats', projectId] });
      setUserInput('');
      setActiveTab('history');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to generate query');
    },
  });

  // Delete query mutation
  const deleteQueryMutation = useMutation({
    mutationFn: (queryId: string) => apiService.deleteQuery(queryId),
    onSuccess: () => {
      toast.success('Query deleted successfully!');
      queryClient.invalidateQueries({ queryKey: ['queries', projectId] });
      queryClient.invalidateQueries({ queryKey: ['project-stats', projectId] });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to delete query');
    },
  });

  const handleGenerateQuery = () => {
    if (!userInput.trim()) {
      toast.error('Please enter a query description');
      return;
    }
    generateQueryMutation.mutate(userInput);
  };

  const handleCopyQuery = async (sql: string) => {
    try {
      await copyToClipboard(sql);
      toast.success('SQL query copied to clipboard!');
    } catch (error) {
      toast.error('Failed to copy query');
    }
  };

  const handleDeleteQuery = (queryId: string) => {
    if (confirm('Are you sure you want to delete this query?')) {
      deleteQueryMutation.mutate(queryId);
    }
  };

  const sampleQueries = [
    "Show me all users who registered in the last 30 days",
    "Find products with low stock (less than 10 items)",
    "Get total sales by category",
    "List orders with their customer information",
    "Find the most popular products"
  ];

  return (
    <div className="min-h-screen">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-4">
              <Button
                variant="ghost"
                onClick={() => navigate(`/project/${projectId}`)}
                className="p-2"
              >
                <ArrowLeft className="h-5 w-5" />
              </Button>
              <div>
                <h1 className="text-3xl font-bold gradient-text">
                  {project?.name} - Queries
                </h1>
                <p className="text-muted-foreground">
                  Generate and manage SQL queries
                </p>
              </div>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="flex space-x-1 bg-white/5 rounded-lg p-1 max-w-md">
            <button
              onClick={() => setActiveTab('generate')}
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'generate'
                  ? 'bg-white/10 text-white'
                  : 'text-muted-foreground hover:text-white'
              }`}
            >
              <Sparkles className="h-4 w-4 inline mr-2" />
              Generate
            </button>
            <button
              onClick={() => setActiveTab('history')}
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'history'
                  ? 'bg-white/10 text-white'
                  : 'text-muted-foreground hover:text-white'
              }`}
            >
              <History className="h-4 w-4 inline mr-2" />
              History
            </button>
          </div>
        </motion.div>

        {/* Generate Query Tab */}
        {activeTab === 'generate' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            {/* Query Generation Form */}
            <Card className="glass-card">
              <CardHeader>
                <CardTitle>Generate SQL Query</CardTitle>
                <CardDescription>
                  Describe what you want to query in natural language
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="user_input">Query Description</Label>
                  <Textarea
                    id="user_input"
                    value={userInput}
                    onChange={(e) => setUserInput(e.target.value)}
                    placeholder="e.g., Show me all users who registered in the last 30 days"
                    rows={4}
                    className="resize-none"
                  />
                </div>

                {/* Sample Queries */}
                <div className="space-y-2">
                  <Label className="text-sm text-muted-foreground">Sample Queries:</Label>
                  <div className="flex flex-wrap gap-2">
                    {sampleQueries.map((sample, index) => (
                      <button
                        key={index}
                        onClick={() => setUserInput(sample)}
                        className="px-3 py-1 text-xs bg-white/5 hover:bg-white/10 rounded-full transition-colors"
                      >
                        {sample}
                      </button>
                    ))}
                  </div>
                </div>

                <Button
                  onClick={handleGenerateQuery}
                  className="gradient w-full"
                  disabled={generateQueryMutation.isPending || !userInput.trim()}
                >
                  {generateQueryMutation.isPending ? (
                    <div className="flex items-center space-x-2">
                      <RefreshCw className="h-4 w-4 animate-spin" />
                      <span>Generating Query...</span>
                    </div>
                  ) : (
                    <div className="flex items-center space-x-2">
                      <Send className="h-4 w-4" />
                      <span>Generate SQL Query</span>
                    </div>
                  )}
                </Button>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Query History Tab */}
        {activeTab === 'history' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            {isLoading ? (
              <div className="space-y-4">
                {[1, 2, 3].map((i) => (
                  <Card key={i} className="glass-card">
                    <CardContent className="p-6">
                      <div className="animate-pulse">
                        <div className="h-4 bg-white/10 rounded w-3/4 mb-2"></div>
                        <div className="h-3 bg-white/10 rounded w-1/2 mb-4"></div>
                        <div className="space-y-2">
                          <div className="h-3 bg-white/10 rounded w-full"></div>
                          <div className="h-3 bg-white/10 rounded w-3/4"></div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : queriesData?.data.length === 0 ? (
              <Card className="glass-card">
                <CardContent className="p-8 text-center">
                  <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-semibold mb-2">No queries yet</h3>
                  <p className="text-muted-foreground mb-6">
                    Generate your first SQL query from natural language
                  </p>
                  <Button 
                    onClick={() => setActiveTab('generate')} 
                    className="gradient"
                  >
                    <Sparkles className="h-4 w-4 mr-2" />
                    Generate Query
                  </Button>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-4">
                {queriesData?.data.map((query) => (
                  <motion.div
                    key={query.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                  >
                    <Card className="glass-card">
                      <CardHeader>
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <p className="text-sm font-medium mb-1">
                              {query.user_input}
                            </p>
                            <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                              <span>{formatDate(query.created_at)}</span>
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleCopyQuery(query.generated_sql)}
                            >
                              <Copy className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => navigate(`/query/${query.id}`)}
                            >
                              <FileText className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleDeleteQuery(query.id)}
                              className="text-destructive"
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-3">
                          <div>
                            <Label className="text-xs text-muted-foreground">Generated SQL:</Label>
                            <pre className="mt-1 p-3 bg-white/5 rounded text-sm overflow-x-auto">
                              {query.generated_sql}
                            </pre>
                          </div>
                          {query.explanation && (
                            <div>
                              <Label className="text-xs text-muted-foreground">Explanation:</Label>
                              <p className="mt-1 text-sm text-muted-foreground">
                                {query.explanation}
                              </p>
                            </div>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                ))}
              </div>
            )}
          </motion.div>
        )}
      </main>
    </div>
  );
}


