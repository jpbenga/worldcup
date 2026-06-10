import { PercentPipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { ScoreMatrix, ScoreProbability } from '../../models/worldcup.models';

@Component({
  selector: 'app-score-matrix',
  imports: [PercentPipe],
  templateUrl: './score-matrix.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ScoreMatrixComponent {
  @Input({ required: true }) matrix!: ScoreMatrix;

  get leadingScores(): ScoreProbability[] {
    return [...this.matrix.probabilities]
      .sort((first, second) => second.probability - first.probability)
      .slice(0, 10);
  }
}
