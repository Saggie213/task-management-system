import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { DndContext, DragOverlay, closestCorners, PointerSensor, useSensor, useSensors } from '@dnd-kit/core';
import { SortableContext, verticalListSortingStrategy, useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { taskAPI } from '../api/tasks';
import TaskModal from '../components/TaskModal';
import { format } from 'date-fns';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [selectedTask, setSelectedTask] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    setLoading(true);
    const result = await taskAPI.getTasks();
    if (result.success) {
      setTasks(result.data);
    } else {
      setError(result.error);
    }
    setLoading(false);
  };

  const handleCreateTask = () => {
    setSelectedTask(null);
    setShowModal(true);
  };

  const handleEditTask = (task) => {
    setSelectedTask(task);
    setShowModal(true);
  };

  const handleDeleteTask = async (taskId) => {
    if (!window.confirm('Are you sure you want to delete this task?')) {
      return;
    }

    const result = await taskAPI.deleteTask(taskId);
    if (result.success) {
      // Update state immediately to remove the task
      setTasks(prevTasks => prevTasks.filter(t => t.id !== taskId));
    } else {
      setError(result.error);
    }
  };

  const handleTaskSaved = (savedTask) => {
    if (selectedTask) {
      // Update existing task
      setTasks(tasks.map(t => t.id === savedTask.id ? savedTask : t));
    } else {
      // Add new task
      setTasks([...tasks, savedTask]);
    }
    setShowModal(false);
    setSelectedTask(null);
  };

  const onDragEnd = async (dragResult) => {
    console.log('onDragEnd called:', dragResult);
    const { destination, source, draggableId } = dragResult;

    // Dropped outside the list
    if (!destination) {
      console.log('Dropped outside list');
      return;
    }

    // No movement
    if (
      destination.droppableId === source.droppableId &&
      destination.index === source.index
    ) {
      console.log('No movement detected');
      return;
    }

    // Get the task being moved
    const task = tasks.find(t => t.id === draggableId);
    const newStatus = destination.droppableId;
    
    console.log(`Moving task "${task?.title}" from ${source.droppableId} to ${newStatus}`);

    // Store original tasks for revert
    const originalTasks = [...tasks];

    // Update locally first for better UX
    const updatedTasks = tasks.map(t => 
      t.id === draggableId ? { ...t, status: newStatus } : t
    );
    setTasks(updatedTasks);

    // Update on backend
    const result = await taskAPI.updateTask(draggableId, { status: newStatus });
    if (!result.success) {
      // Revert on error
      console.error('Failed to update task:', result.error);
      setError(result.error);
      setTasks(originalTasks);
    } else {
      console.log('Task status updated successfully');
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const getTasksByStatus = (status) => {
    return tasks.filter(task => task.status === status);
  };

  const columns = [
    { id: 'pending', title: 'Pending', bgColor: 'bg-yellow-50', borderColor: 'border-yellow-200' },
    { id: 'in-progress', title: 'In Progress', bgColor: 'bg-blue-50', borderColor: 'border-blue-200' },
    { id: 'completed', title: 'Completed', bgColor: 'bg-green-50', borderColor: 'border-green-200' }
  ];

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-xl text-gray-600">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900" data-testid="dashboard-title">Task Board</h1>
              <p className="text-sm text-gray-600 mt-1">Welcome, {user?.username}!</p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={handleCreateTask}
                className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
                data-testid="create-task-button"
              >
                + New Task
              </button>
              <button
                onClick={() => navigate('/profile')}
                className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
                data-testid="profile-button"
              >
                Profile
              </button>
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
                data-testid="dashboard-logout-button"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-4">
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md" data-testid="dashboard-error-message">
            {error}
          </div>
        </div>
      )}

      {/* Kanban Board */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <DragDropContext onDragEnd={onDragEnd}>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {columns.map(column => (
              <div key={column.id} className="flex flex-col" data-testid={`column-${column.id}`}>
                <div className="mb-4">
                  <h2 className="text-lg font-semibold text-gray-900">{column.title}</h2>
                  <p className="text-sm text-gray-500">{getTasksByStatus(column.id).length} tasks</p>
                </div>

                <Droppable droppableId={column.id} isDropDisabled={false} isCombineEnabled={false}>
                  {(provided, snapshot) => (
                    <div
                      ref={provided.innerRef}
                      {...provided.droppableProps}
                      className={`flex-1 rounded-lg p-4 min-h-[500px] transition-colors ${
                        snapshot.isDraggingOver ? column.bgColor : 'bg-gray-100'
                      }`}
                      data-testid={`droppable-${column.id}`}
                    >
                      {getTasksByStatus(column.id).map((task, index) => (
                        <Draggable key={task.id} draggableId={task.id} index={index}>
                          {(provided, snapshot) => (
                            <div
                              ref={provided.innerRef}
                              {...provided.draggableProps}
                              {...provided.dragHandleProps}
                              className={`bg-white rounded-lg shadow-sm border p-4 mb-3 cursor-move transition-shadow ${
                                snapshot.isDragging ? 'shadow-lg' : 'hover:shadow-md'
                              } ${column.borderColor}`}
                              data-testid={`task-card-${task.id}`}
                            >
                              <h3 className="font-semibold text-gray-900 mb-2" data-testid={`task-title-${task.id}`}>
                                {task.title}
                              </h3>
                              {task.description && (
                                <p className="text-sm text-gray-600 mb-3 line-clamp-2" data-testid={`task-description-${task.id}`}>
                                  {task.description}
                                </p>
                              )}
                              {task.due_date && (
                                <div className="flex items-center text-xs text-gray-500 mb-3" data-testid={`task-due-date-${task.id}`}>
                                  <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                  </svg>
                                  Due: {format(new Date(task.due_date), 'MMM dd, yyyy')}
                                </div>
                              )}
                              <div className="flex gap-2">
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleEditTask(task);
                                  }}
                                  className="flex-1 px-3 py-1 text-sm bg-indigo-50 text-indigo-600 rounded hover:bg-indigo-100 transition-colors"
                                  data-testid={`edit-task-button-${task.id}`}
                                >
                                  Edit
                                </button>
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleDeleteTask(task.id);
                                  }}
                                  className="flex-1 px-3 py-1 text-sm bg-red-50 text-red-600 rounded hover:bg-red-100 transition-colors"
                                  data-testid={`delete-task-button-${task.id}`}
                                >
                                  Delete
                                </button>
                              </div>
                            </div>
                          )}
                        </Draggable>
                      ))}
                      {provided.placeholder}
                    </div>
                  )}
                </Droppable>
              </div>
            ))}
          </div>
        </DragDropContext>
      </div>

      {/* Task Modal */}
      {showModal && (
        <TaskModal
          task={selectedTask}
          onClose={() => {
            setShowModal(false);
            setSelectedTask(null);
          }}
          onSave={handleTaskSaved}
        />
      )}
    </div>
  );
};

export default Dashboard;
