import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { Team } from '../../models/team.model';
import { Subject } from '../../models/subject.model';

@Component({
  selector: 'app-teams',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './teams.component.html',
  styleUrls: ['./teams.component.css']
})
export class TeamsComponent implements OnInit {
  teams: Team[] = [];
  subjects: Subject[] = [];
  newTeamName = '';
  selectedSubjectId: number | null = null;
  error = '';

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.api.getTeams().subscribe({
      next: (t) => this.teams = t,
      error: () => this.error = 'Failed to load teams'
    });
    this.api.getSubjects().subscribe({
      next: (s) => this.subjects = s,
      error: () => this.error = 'Failed to load subjects'
    });
  }

  createTeam(): void {
    if (!this.newTeamName || !this.selectedSubjectId) {
      this.error = 'Please fill team name and select a subject';
      return;
    }
    this.api.createTeam(this.newTeamName, this.selectedSubjectId).subscribe({
      next: (t) => {
        this.teams.push(t);
        this.newTeamName = '';
        this.selectedSubjectId = null;
        this.error = '';
      },
      error: () => this.error = 'Failed to create team'
    });
  }

  deleteTeam(id: number): void {
    this.api.deleteTeam(id).subscribe({
      next: () => this.teams = this.teams.filter(t => t.id !== id),
      error: () => this.error = 'Failed to delete team'
    });
  }
}