import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { Task, TaskStatus, CreateTaskDto } from '../../models/task.model';

@Component({
  selector: 'app-board',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './board.component.html',
  styleUrls: ['./board.component.css']
})
export class BoardComponent implements OnInit {
  teamId!: number;
  tasks: Task[] = [];
  columns: TaskStatus[] = ['todo', 'in_progress', 'review', 'done'];
  columnLabels: Record<TaskStatus, string> = {
    todo: '📝 To Do',
    in_progress: '🔄 In Progress',
    review: '👁 Review',
    done: '✅ Done'
  };

  showModal = false;
  selectedTask: Task | null = null;
  newComment = '';
  error = '';

  newTask: CreateTaskDto = {
    title: '', description: '', status: 'todo',
    priority: 'medium', deadline: null, team: 0
  };

  constructor(private api: ApiService, private route: ActivatedRoute) {}

  ngOnInit(): void {
    this.teamId = Number(this.route.snapshot.paramMap.get('id'));
    this.newTask.team = this.teamId;
    this.loadTasks();
  }

  loadTasks(): void {
    this.api.getTasks(this.teamId).subscribe({
      next: (t) => this.tasks = t,
      error: () => this.error = 'Failed to load tasks'
    });
  }

  getTasksByStatus(status: TaskStatus): Task[] {
    return this.tasks.filter(t => t.status === status);
  }

  createTask(): void {
    this.api.createTask(this.newTask).subscribe({
      next: (t) => {
        this.tasks.push(t);
        this.newTask = {
          title: '', description: '', status: 'todo',
          priority: 'medium', deadline: null, team: this.teamId
        };
      },
      error: () => this.error = 'Failed to create task'
    });
  }

  moveTask(task: Task, newStatus: TaskStatus): void {
    this.api.updateTaskStatus(task.id, newStatus).subscribe({
      next: (updated) => {
        const idx = this.tasks.findIndex(t => t.id === task.id);
        if (idx !== -1) this.tasks[idx] = updated;
      },
      error: () => this.error = 'Failed to update status'
    });
  }

  openTask(task: Task): void {
    this.selectedTask = task;
    this.showModal = true;
  }

  closeModal(): void {
    this.showModal = false;
    this.selectedTask = null;
    this.newComment = '';
  }

  addComment(): void {
    if (!this.selectedTask || !this.newComment.trim()) return;
    this.api.addComment(this.selectedTask.id, this.newComment).subscribe({
      next: (c) => {
        this.selectedTask!.comments.push(c);
        this.newComment = '';
      },
      error: () => this.error = 'Failed to add comment'
    });
  }

  deleteTask(id: number): void {
    this.api.deleteTask(id).subscribe({
      next: () => {
        this.tasks = this.tasks.filter(t => t.id !== id);
        this.closeModal();
      },
      error: () => this.error = 'Failed to delete task'
    });
  }
}