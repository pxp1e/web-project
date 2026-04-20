import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { Task, TaskStatus, CreateTaskDto } from '../../models/task.model';
import { NavbarComponent } from '../../components/navbar/navbar';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-board',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, NavbarComponent],
  templateUrl: './board.component.html',
  styleUrls: ['./board.component.css']
})
export class BoardComponent implements OnInit {
  teamId!: number;
  tasks: Task[] = [];
  teamMembers: any[] = [];
  columns: TaskStatus[] = ['todo', 'in_progress', 'review', 'done'];
  columnLabels: Record<TaskStatus, string> = {
    todo: '📝 To Do',
    in_progress: '🔄 In Progress',
    review: '👁 Review',
    done: '✅ Done'
  };
  currentUser: any = null;
  isAdmin = false;
  showModal = false;
  selectedTask: any = null;
  newComment = '';
  error = '';

  newTask: any = {
  title: '', description: '', status: 'todo',
  priority: 'medium', 
  deadline: new Date(new Date().getTime() - new Date().getTimezoneOffset() * 60000).toISOString().split('T')[0],
  team: 0, 
  assigned_to_id: null
};

  constructor(
    private api: ApiService,
    private route: ActivatedRoute,
    private cdr: ChangeDetectorRef,
    private auth: AuthService
  ) {}

  ngOnInit(): void {
  this.teamId = Number(this.route.snapshot.paramMap.get('id'));
  this.newTask.team = this.teamId;
  
  const user = this.auth['userSubject'].getValue();
  if (user) {
    this.currentUser = user;
    this.loadTeamInfo();
    this.loadTasks();
  } else {
    this.auth.user$.subscribe(u => {
      if (u && !this.currentUser) {
        this.currentUser = u;
        this.loadTeamInfo();
        this.loadTasks();
      }
    });
  }

  this.route.queryParams.subscribe(params => {
    if (params['taskId']) {
      const taskId = Number(params['taskId']);
      setTimeout(() => {
        const task = this.tasks.find(t => t.id === taskId);
        if (task) {
          this.openTask(task);
          this.cdr.detectChanges();
        }
      }, 500);
    }
  });
}

  loadTeamInfo(): void {
    this.api.getTeamMembers(this.teamId).subscribe({
      next: (team: any) => {
        this.teamMembers = team.memberships || [];
        const myMembership = this.teamMembers.find(
          (m: any) => m.user.username === this.currentUser?.username
        );
        this.isAdmin = myMembership?.role === 'admin';
        this.cdr.detectChanges();
      },
      error: () => {}
    });
  }

  loadTasks(): void {
    this.api.getTasks(this.teamId).subscribe({
      next: (t) => { this.tasks = [...t]; this.cdr.detectChanges(); },
      error: () => this.error = 'Failed to load tasks'
    });
  }

  getTasksByStatus(status: TaskStatus): Task[] {
    return this.tasks.filter(t => t.status === status);
  }

  createTask(): void {
  this.error = '';
  if (!this.newTask.title.trim()) {
    this.error = 'Task title is required';
    return;
  }
  if (!this.newTask.deadline) {
    this.newTask.deadline = new Date().toISOString().split('T')[0];
  }
  this.api.createTask(this.newTask).subscribe({
    next: (t) => {
      this.tasks = [...this.tasks, t];
      this.newTask = {
        title: '', description: '', status: 'todo',
        priority: 'medium',
        deadline: new Date().toISOString().split('T')[0],
        team: this.teamId,
        assigned_to_id: null
      };
      this.error = '';
      this.cdr.detectChanges();
    },
    error: (err) => {
      this.error = err.error?.error || 'Failed to create task';
    }
  });
}

  moveTask(task: Task, newStatus: TaskStatus): void {
    this.api.updateTaskStatus(task.id, newStatus).subscribe({
      next: (updated) => {
        this.tasks = this.tasks.map(t => t.id === task.id ? updated : t);
        this.cdr.detectChanges();
      },
      error: () => this.error = 'Failed to update status'
    });
  }

  openTask(task: Task): void {
  this.selectedTask = { 
    ...task,
    comments: task.comments.map(c => ({ ...c }))
  };
  this.showModal = true;
  this.cdr.detectChanges();
}

  closeModal(): void {
    this.showModal = false;
    this.selectedTask = null;
    this.newComment = '';
    this.cdr.detectChanges();
  }

  addComment(): void {
    if (!this.selectedTask || !this.newComment.trim()) return;
    this.api.addComment(this.selectedTask.id, this.newComment).subscribe({
      next: (c) => {
        this.selectedTask!.comments = [...this.selectedTask!.comments, c];
        this.newComment = '';
        this.cdr.detectChanges();
      },
      error: () => this.error = 'Failed to add comment'
    });
  }

  deleteComment(commentId: number): void {
    if (!this.selectedTask) return;
    if (!confirm('Are you sure you want to delete this comment?')) return;
    this.api.deleteComment(this.selectedTask.id, commentId).subscribe({
      next: () => {
        this.selectedTask!.comments = this.selectedTask!.comments.filter(c => c.id !== commentId);
        this.cdr.detectChanges();
      },
      error: () => this.error = 'Failed to delete comment'
    });
  }

  deleteTask(id: number): void {
    if (!confirm('Are you sure you want to delete this task?')) return;
    this.api.deleteTask(id).subscribe({
      next: () => {
        this.tasks = this.tasks.filter(t => t.id !== id);
        this.closeModal();
        this.cdr.detectChanges();
      },
      error: () => this.error = 'Failed to delete task'
    });
  }

  changeAssignee(event: any): void {
  if (!this.selectedTask || !event.target.value) return;
  const userId = Number(event.target.value);
  this.api.updateTask(this.selectedTask.id, { assigned_to_id: userId }).subscribe({
    next: (updated) => {
      this.selectedTask = { ...updated, comments: this.selectedTask!.comments };
      this.tasks = this.tasks.map(t => t.id === updated.id ? updated : t);
    },
    error: () => this.error = 'Failed to change assignee'
  });
}

likeComment(comment: any): void {
  console.log('liking comment:', comment.id);
  this.api.likeComment(comment.id).subscribe({
    next: (res) => {
      console.log('like response:', res);
      if (this.selectedTask) {
        this.selectedTask = {
          ...this.selectedTask,
          comments: this.selectedTask.comments.map((c: any) =>
            c.id === comment.id
              ? { ...c, likes_count: res.likes_count, is_liked: res.liked }
              : c
          )
        };
        this.cdr.detectChanges();
      }
    },
    error: (err) => { 
      console.log('like error:', err);
      this.error = 'Failed to like comment'; 
    }
  });
}
}