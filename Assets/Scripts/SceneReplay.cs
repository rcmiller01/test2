using UnityEngine;
using UnityEngine.Playables;

public class SceneReplay : MonoBehaviour
{
    public Animator animator;
    public PlayableDirector kneelTimeline;
    public PlayableDirector flameTimeline;

    public void PlayScene(string clipID)
    {
        Debug.Log("Replaying scene: " + clipID);

        if (clipID.Contains("kneel"))
        {
            animator.Play("Scene_Kneel");
            if (kneelTimeline != null)
                kneelTimeline.Play();
        }
        else if (clipID.Contains("flame"))
        {
            animator.Play("Scene_FlameBurst");
            if (flameTimeline != null)
                flameTimeline.Play();
        }
        else
        {
            animator.Play("Scene_IdleLoop");
        }
    }
}
