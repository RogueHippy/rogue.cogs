# project_zomboid_restart/__init__.py
from .project_zomboid_restart import ProjectZomboidRestart

def setup(bot):
    bot.add_cog(ProjectZomboidRestart(bot))
