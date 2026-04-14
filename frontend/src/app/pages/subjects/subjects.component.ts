import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { Subject } from '../../models/subject.model';

@Component({
  selector: 'app-subjects',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './subjects.component.html',
  styleUrls: ['./subjects.component.css']
})
export class SubjectsComponent implements OnInit {
  subjects: Subject[] = [];
  form = { name: '', code: '', semester: 1 };
  error = '';

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.api.getSubjects().subscribe({
      next: (s) => this.subjects = s,
      error: () => this.error = 'Failed to load subjects'
    });
  }

  createSubject(): void {
    this.api.createSubject(this.form).subscribe({
      next: (s) => {
        this.subjects.push(s);
        this.form = { name: '', code: '', semester: 1 };
        this.error = '';
      },
      error: () => this.error = 'Failed to create subject'
    });
  }

  deleteSubject(id: number): void {
    this.api.deleteSubject(id).subscribe({
      next: () => this.subjects = this.subjects.filter(s => s.id !== id),
      error: () => this.error = 'Failed to delete subject'
    });
  }
}