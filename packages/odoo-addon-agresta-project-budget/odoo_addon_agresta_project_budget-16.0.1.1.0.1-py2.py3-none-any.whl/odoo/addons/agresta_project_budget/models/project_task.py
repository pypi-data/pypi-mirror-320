# Copyright 2024 - Coopdevs - Quim Rebull
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class Task(models.Model):

    _inherit = "project.task"


    task_update_ids=fields.One2many(
        string="Task updates",
        comodel_name="project.task.update",
        inverse_name="task_id"
    )
    budget_amount = fields.Monetary(
        string="Budget Amount",
        currency_field='currency_id',
        help="Amount asigned to this task",
    ) 
    subtasks_budget_amount = fields.Monetary(
        "Subtasks Budget Amount", 
        compute='_compute_subtask_effective_hours', 
        recursive=True, 
        store=True, 
        help="Amount asigned on subtasks",
        currency_field='currency_id'
    )

    execution_pcnt = fields.Float(
       string="Execution percent",
       help="Execution percent of the task",       
       compute="_get_last_update",
       store=True     
    ) 
    currency_id = fields.Many2one(
        related="project_id.analytic_account_id.company_id.currency_id",
        string="Currency",
    )

    project_execution_weight = fields.Selection(related="project_id.execution_weight",store=1)


    @api.depends('task_update_ids.date','task_update_ids.execution_pcnt')
    def _get_last_update(self):
        date_compare = False
        selected=False
        for rec in self:
            for tu in rec.task_update_ids:
                if (not date_compare and tu.date) or tu.date> date_compare:
                    selected=tu
            if selected and selected.date and selected.execution_pcnt:
                rec.execution_pcnt=selected.execution_pcnt
                
    @api.depends('child_ids.budget_amount', 'child_ids.subtasks_budget_amount')
    def _compute_subtask_effective_hours(self):
        for task in self.with_context(active_test=False):
            task.subtasks_budget_amount = sum(child_task.budget_amount + child_task.subtasks_budget_amount for child_task in task.child_ids)
    

